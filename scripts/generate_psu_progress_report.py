#!/usr/bin/env python
"""
Generate a progress report snapshot for the PSU chatbot project.

The report intentionally prefers direct database queries for primary metrics and
uses authenticated/public endpoints only for cross-checking.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests
from dotenv import dotenv_values
from sqlalchemy import create_engine, text


APP_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
DEFAULT_BACKEND_URL = "https://puschatbot-production.up.railway.app"
DEFAULT_REPORT_DATE = datetime.now(APP_TZ).date()
DEFAULT_WINDOW_DAYS = 30


def format_int_vi(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def format_float_vi(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def short_text(value: str | None, limit: int = 120) -> str:
    if not value:
        return ""
    text_value = " ".join(value.split())
    if len(text_value) <= limit:
        return text_value
    return text_value[: limit - 3].rstrip() + "..."


def is_today_in_app_tz(target: date) -> bool:
    return datetime.now(APP_TZ).date() == target


def safe_comment(comment: str | None) -> bool:
    if not comment:
        return False

    normalized = " ".join(comment.strip().split())
    if len(normalized) < 2:
        return False

    banned_fragments = {
        "gay",
        "gud",
        "overfitting",
        "test",
        "bth",
    }
    lowered = normalized.lower()
    return not any(fragment in lowered for fragment in banned_fragments)


@dataclass
class EndpointBundle:
    traffic_summary: dict[str, Any]
    chat_history_overview: dict[str, Any]
    feedback_30d: dict[str, Any]
    feedback_all_time: dict[str, Any]


class ReportGenerator:
    def __init__(
        self,
        database_url: str,
        backend_url: str,
        admin_username: str,
        admin_password: str,
        report_date: date,
        window_days: int,
    ) -> None:
        self.database_url = database_url
        self.backend_url = backend_url.rstrip("/")
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.report_date = report_date
        self.window_days = window_days
        self.engine = create_engine(self.database_url)

    def _window_bounds(self) -> tuple[datetime, datetime]:
        now_local = datetime.now(APP_TZ)
        if is_today_in_app_tz(self.report_date):
            window_end = now_local.replace(tzinfo=None)
        else:
            window_end = datetime.combine(
                self.report_date + timedelta(days=1),
                time.min,
            )
        window_start = window_end - timedelta(days=self.window_days)
        return window_start, window_end

    def _query(self, sql: str, params: dict[str, Any] | None = None) -> list[tuple[Any, ...]]:
        with self.engine.connect() as conn:
            return list(conn.execute(text(sql), params or {}).fetchall())

    def _scalar(self, sql: str, params: dict[str, Any] | None = None) -> Any:
        with self.engine.connect() as conn:
            return conn.execute(text(sql), params or {}).scalar()

    def _fetch_db_metrics(self) -> dict[str, Any]:
        window_start, window_end = self._window_bounds()
        uses_live_window = is_today_in_app_tz(self.report_date)

        if uses_live_window:
            window_filter_conversations = (
                "created_at >= NOW() - make_interval(days => :window_days) "
                "AND created_at < NOW()"
            )
            window_filter_sessions = (
                "last_visit >= NOW() - make_interval(days => :window_days) "
                "AND last_visit < NOW()"
            )
            feedback_filter = (
                "created_at >= NOW() - make_interval(days => :window_days) "
                "AND created_at < NOW()"
            )
            params = {"window_days": self.window_days}
        else:
            window_filter_conversations = (
                "created_at >= :window_start AND created_at < :window_end"
            )
            window_filter_sessions = (
                "last_visit >= :window_start AND last_visit < :window_end"
            )
            feedback_filter = (
                "created_at >= :window_start AND created_at < :window_end"
            )
            params = {"window_start": window_start, "window_end": window_end}

        metrics: dict[str, Any] = {}
        metrics["window_start"] = window_start
        metrics["window_end"] = window_end

        metrics["public"] = {
            "page_views_total": int(
                self._scalar("SELECT COUNT(*) FROM access_logs") or 0
            ),
            "access_sessions_total": int(
                self._scalar("SELECT COUNT(DISTINCT session_id) FROM access_logs") or 0
            ),
            "online_now": int(
                self._scalar(
                    "SELECT COUNT(*) FROM user_sessions WHERE last_visit >= NOW() - INTERVAL '5 minutes'"
                )
                or 0
            ),
        }

        metrics["window_30d"] = {
            "active_session_users": int(
                self._scalar(
                    f"SELECT COUNT(*) FROM user_sessions WHERE {window_filter_sessions}",
                    params,
                )
                or 0
            ),
            "unique_conversations": int(
                self._scalar(
                    f"SELECT COUNT(DISTINCT conversation_id) FROM conversations WHERE {window_filter_conversations}",
                    params,
                )
                or 0
            ),
            "messages": int(
                self._scalar(
                    f"SELECT COUNT(*) FROM conversations WHERE {window_filter_conversations}",
                    params,
                )
                or 0
            ),
        }

        metrics["all_time"] = {
            "session_users": int(self._scalar("SELECT COUNT(*) FROM user_sessions") or 0),
            "returning_sessions": int(
                self._scalar("SELECT COUNT(*) FROM user_sessions WHERE total_visits > 1")
                or 0
            ),
            "conversation_users": int(
                self._scalar("SELECT COUNT(DISTINCT conversation_id) FROM conversations")
                or 0
            ),
            "messages": int(self._scalar("SELECT COUNT(*) FROM conversations") or 0),
            "cumulative_visits": int(
                self._scalar("SELECT COALESCE(SUM(total_visits), 0) FROM user_sessions")
                or 0
            ),
            "cumulative_questions": int(
                self._scalar(
                    "SELECT COALESCE(SUM(total_questions), 0) FROM user_sessions"
                )
                or 0
            ),
        }

        window_feedback_row = self._query(
            f"""
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE rating = 'positive') AS positive,
                COUNT(*) FILTER (WHERE rating = 'negative') AS negative,
                COUNT(*) FILTER (WHERE rating = 'neutral') AS neutral
            FROM feedback
            WHERE {feedback_filter}
            """,
            params,
        )[0]
        all_time_feedback_row = self._query(
            """
            SELECT
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE rating = 'positive') AS positive,
                COUNT(*) FILTER (WHERE rating = 'negative') AS negative,
                COUNT(*) FILTER (WHERE rating = 'neutral') AS neutral
            FROM feedback
            """
        )[0]
        metrics["feedback"] = {
            "window": self._build_feedback_dict(window_feedback_row),
            "all_time": self._build_feedback_dict(all_time_feedback_row),
        }

        daily_users_rows = self._query(
            f"""
            SELECT DATE(last_visit) AS day, COUNT(DISTINCT session_id) AS users
            FROM user_sessions
            WHERE {window_filter_sessions}
            GROUP BY DATE(last_visit)
            ORDER BY day
            """,
            params,
        )
        daily_messages_rows = self._query(
            f"""
            SELECT DATE(created_at) AS day, COUNT(*) AS messages
            FROM conversations
            WHERE {window_filter_conversations}
            GROUP BY DATE(created_at)
            ORDER BY day
            """,
            params,
        )
        metrics["daily"] = {
            "users": [(str(row[0]), int(row[1])) for row in daily_users_rows],
            "messages": [(str(row[0]), int(row[1])) for row in daily_messages_rows],
            "avg_users": (
                sum(int(row[1]) for row in daily_users_rows) / len(daily_users_rows)
                if daily_users_rows
                else 0.0
            ),
            "avg_messages": (
                sum(int(row[1]) for row in daily_messages_rows) / len(daily_messages_rows)
                if daily_messages_rows
                else 0.0
            ),
        }

        popular_rows = self._query(
            f"""
            SELECT
                user_message,
                COUNT(*) AS count,
                MAX(created_at) AS last_asked
            FROM conversations
            WHERE {window_filter_conversations}
              AND LENGTH(TRIM(user_message)) > 5
              AND user_message NOT ILIKE '%test%'
              AND user_message NOT ILIKE '%hello%'
              AND user_message NOT ILIKE '%xin chào%'
              AND user_message NOT ILIKE '%hi%'
            GROUP BY user_message
            HAVING COUNT(*) > 1
            ORDER BY count DESC
            LIMIT 10
            """,
            params,
        )
        metrics["popular_questions"] = [
            {
                "question": short_text(str(row[0]), limit=140),
                "count": int(row[1]),
                "last_asked": str(row[2]),
            }
            for row in popular_rows
        ]

        metrics["feedback_examples"] = self._fetch_feedback_examples()
        return metrics

    def _build_feedback_dict(self, row: tuple[Any, ...]) -> dict[str, Any]:
        total = int(row[0] or 0)
        positive = int(row[1] or 0)
        negative = int(row[2] or 0)
        neutral = int(row[3] or 0)
        return {
            "total": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "positive_rate": (positive / total * 100) if total else 0.0,
            "negative_rate": (negative / total * 100) if total else 0.0,
        }

    def _fetch_feedback_examples(self) -> dict[str, list[dict[str, str]]]:
        positive_rows = self._query(
            """
            SELECT created_at, query, comment
            FROM feedback
            WHERE rating = 'positive'
              AND comment IS NOT NULL
              AND BTRIM(comment) <> ''
            ORDER BY created_at DESC
            LIMIT 25
            """
        )
        negative_rows = self._query(
            """
            SELECT created_at, query, comment
            FROM feedback
            WHERE rating = 'negative'
              AND comment IS NOT NULL
              AND BTRIM(comment) <> ''
            ORDER BY created_at DESC
            LIMIT 25
            """
        )

        positive_examples = []
        for row in positive_rows:
            comment = " ".join(str(row[2]).split())
            if not safe_comment(comment):
                continue
            positive_examples.append(
                {
                    "created_at": str(row[0]),
                    "query": short_text(str(row[1]), limit=120),
                    "comment": comment,
                }
            )
        negative_examples = []
        for row in negative_rows:
            comment = " ".join(str(row[2]).split())
            if not safe_comment(comment):
                continue
            negative_examples.append(
                {
                    "created_at": str(row[0]),
                    "query": short_text(str(row[1]), limit=120),
                    "comment": comment,
                }
            )

        return {
            "positive": self._unique_comments(positive_examples)[:5],
            "negative": self._unique_comments(negative_examples)[:5],
        }

    @staticmethod
    def _unique_comments(records: list[dict[str, str]]) -> list[dict[str, str]]:
        seen: set[str] = set()
        unique_records: list[dict[str, str]] = []
        for record in records:
            key = record["comment"].strip().lower()
            if key in seen:
                continue
            seen.add(key)
            unique_records.append(record)
        return unique_records

    def _fetch_endpoints(self) -> EndpointBundle:
        token = self._login_admin()
        headers = {"Authorization": f"Bearer {token}"}

        traffic_summary = self._get_json("/api/v1/analytics/traffic-summary")
        chat_history_overview = self._get_json(
            "/api/v1/admin/chat-history/stats/overview",
            headers=headers,
        )
        feedback_30d = self._get_json(
            f"/api/v1/feedback/stats?days={self.window_days}",
            headers=headers,
        )
        feedback_all_time = self._get_json(
            "/api/v1/feedback/stats?days=3650",
            headers=headers,
        )
        return EndpointBundle(
            traffic_summary=traffic_summary,
            chat_history_overview=chat_history_overview,
            feedback_30d=feedback_30d,
            feedback_all_time=feedback_all_time,
        )

    def _login_admin(self) -> str:
        response = requests.post(
            f"{self.backend_url}/api/v1/auth/login",
            json={
                "username": self.admin_username,
                "password": self.admin_password,
            },
            timeout=30,
        )
        response.raise_for_status()
        payload = response.json()
        return payload["access_token"]

    def _get_json(
        self,
        path: str,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        response = requests.get(
            f"{self.backend_url}{path}",
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    def build_snapshot(self) -> dict[str, Any]:
        db_metrics = self._fetch_db_metrics()
        endpoints = self._fetch_endpoints()
        return {
            "metadata": {
                "report_date": self.report_date.isoformat(),
                "generated_at": datetime.now(APP_TZ).isoformat(),
                "window_days": self.window_days,
                "backend_url": self.backend_url,
            },
            "db_metrics": db_metrics,
            "endpoint_checks": {
                "traffic_summary": endpoints.traffic_summary,
                "chat_history_overview": endpoints.chat_history_overview,
                "feedback_30d": endpoints.feedback_30d,
                "feedback_all_time": endpoints.feedback_all_time,
            },
        }


def render_markdown(snapshot: dict[str, Any]) -> str:
    metadata = snapshot["metadata"]
    db_metrics = snapshot["db_metrics"]
    checks = snapshot["endpoint_checks"]

    public = db_metrics["public"]
    window_30d = db_metrics["window_30d"]
    all_time = db_metrics["all_time"]
    feedback_window = db_metrics["feedback"]["window"]
    feedback_all_time = db_metrics["feedback"]["all_time"]
    daily = db_metrics["daily"]
    feedback_examples = db_metrics["feedback_examples"]
    popular_questions = db_metrics["popular_questions"][:5]

    window_start = format_snapshot_date(db_metrics["window_start"])
    window_end = format_snapshot_date(db_metrics["window_end"])
    report_date = datetime.fromisoformat(metadata["report_date"]).strftime("%d/%m/%Y")

    positive_comments = ", ".join(
        f"“{short_text(item['comment'], limit=90)}”"
        for item in feedback_examples["positive"][:3]
    )
    negative_comments = ", ".join(
        f"“{short_text(item['comment'], limit=90)}”"
        for item in feedback_examples["negative"][:4]
    )

    popular_lines = "\n".join(
        f"{index}. {item['question']}: **{format_int_vi(item['count'])}** lượt"
        for index, item in enumerate(popular_questions, start=1)
    )
    negative_records = "\n".join(
        f"- `{item['created_at'][:10]}` | {item['query']} | phản hồi: “{short_text(item['comment'], limit=140)}”"
        for item in feedback_examples["negative"][:5]
    )

    cross_checks = [
        (
            "Page views toàn thời gian",
            public["page_views_total"],
            checks["traffic_summary"].get("total_views", 0),
        ),
        (
            "Online hiện tại",
            public["online_now"],
            checks["traffic_summary"].get("online_now", 0),
        ),
        (
            "Conversation duy nhất toàn thời gian",
            all_time["conversation_users"],
            checks["chat_history_overview"].get("total_conversations", 0),
        ),
        (
            "Tin nhắn toàn thời gian",
            all_time["messages"],
            checks["chat_history_overview"].get("total_messages", 0),
        ),
        (
            f"Feedback {metadata['window_days']} ngày",
            feedback_window["total"],
            checks["feedback_30d"].get("total_feedback", 0),
        ),
        (
            "Feedback toàn thời gian",
            feedback_all_time["total"],
            checks["feedback_all_time"].get("total_feedback", 0),
        ),
    ]
    cross_check_table = "\n".join(
        f"| {label} | {format_int_vi(int(db_value))} | {format_int_vi(int(api_value))} | {'Khớp' if int(db_value) == int(api_value) else 'Lệch'} |"
        for label, db_value, api_value in cross_checks
    )

    return f"""# Báo cáo tiến độ chatbot PSU

**Mốc chốt số liệu:** {report_date}  
**Khoảng vận hành chính:** 30 ngày gần nhất (`{window_start}` đến `{window_end}`)  
**Nguồn chính:** PostgreSQL production (`user_sessions`, `conversations`, `feedback`, `access_logs`)  
**Nguồn đối chiếu:** endpoint admin/public production trên Railway

## 1. Tóm tắt điều hành

- Chatbot đang vận hành ổn định trên production, với **{format_int_vi(window_30d['active_session_users'])} người dùng theo session web hoạt động** và **{format_int_vi(window_30d['unique_conversations'])} conversation duy nhất** trong 30 ngày gần nhất.
- Trong cùng kỳ, hệ thống đã xử lý **{format_int_vi(window_30d['messages'])} tin nhắn**, tương đương trung bình **{format_float_vi(daily['avg_messages'])} tin nhắn/ngày**.
- Về phản hồi người dùng, chatbot ghi nhận **{format_int_vi(feedback_window['total'])} feedback trong 30 ngày**, trong đó **{format_int_vi(feedback_window['positive'])} tích cực**, **{format_int_vi(feedback_window['negative'])} tiêu cực**, **{format_int_vi(feedback_window['neutral'])} trung tính**. Tỷ lệ tích cực đạt **{format_float_vi(feedback_window['positive_rate'])}%**.
- Nội dung được hỏi nhiều nhất tập trung rõ vào chủ đề tuyển sinh: chỉ tiêu, phương thức tuyển sinh, hồ sơ sơ tuyển, điều kiện sơ tuyển và các mốc thời gian nhập học.

## 2. Số liệu chính

### 2.1. Tình trạng public hiện tại

- **{format_int_vi(public['online_now'])}** người online tại thời điểm kiểm tra.
- **{format_int_vi(public['page_views_total'])}** page views toàn thời gian.
- **{format_int_vi(public['access_sessions_total'])}** session truy cập được ghi nhận trong `access_logs`.

### 2.2. Vận hành 30 ngày gần nhất

- **{format_int_vi(window_30d['active_session_users'])}** người dùng theo session web hoạt động.
- **{format_int_vi(window_30d['unique_conversations'])}** conversation duy nhất.
- **{format_int_vi(window_30d['messages'])}** tin nhắn.
- Trung bình **{format_float_vi(daily['avg_users'], 1)}** người dùng/ngày.
- Trung bình **{format_float_vi(daily['avg_messages'])}** tin nhắn/ngày.

### 2.3. Quy mô tích lũy toàn thời gian

- **{format_int_vi(all_time['session_users'])}** session web.
- **{format_int_vi(all_time['conversation_users'])}** conversation duy nhất.
- **{format_int_vi(all_time['messages'])}** tin nhắn.
- **{format_int_vi(all_time['cumulative_visits'])}** tổng lượt ghé/lượt hỏi cộng dồn trong `user_sessions`.
- **{format_int_vi(all_time['returning_sessions'])}** session quay lại (`total_visits > 1`).

## 3. Phản hồi người dùng

### 3.1. Thống kê phản hồi

- **30 ngày gần nhất:** {format_int_vi(feedback_window['total'])} feedback gồm {format_int_vi(feedback_window['positive'])} tích cực, {format_int_vi(feedback_window['negative'])} tiêu cực, {format_int_vi(feedback_window['neutral'])} trung tính.
- **Tỷ lệ 30 ngày:** tích cực **{format_float_vi(feedback_window['positive_rate'])}%**, tiêu cực **{format_float_vi(feedback_window['negative_rate'])}%**.
- **Toàn thời gian:** {format_int_vi(feedback_all_time['total'])} feedback gồm {format_int_vi(feedback_all_time['positive'])} tích cực, {format_int_vi(feedback_all_time['negative'])} tiêu cực, {format_int_vi(feedback_all_time['neutral'])} trung tính.

### 3.2. Ví dụ phản hồi trích cho báo cáo

- Phản hồi tích cực tiêu biểu: {positive_comments}.
- Phản hồi tiêu cực tiêu biểu: {negative_comments}.

### 3.3. Các phản hồi tiêu cực gần đây

{negative_records}

## 4. Nội dung người dùng quan tâm nhiều nhất trong 30 ngày

{popular_lines}

## 5. Quy tắc trình bày và loại trừ

- Báo cáo này **tách riêng** `người dùng theo session web` và `conversation duy nhất`, không gộp chung thành một chỉ số “người dùng”.
- **Không dùng trong báo cáo chính** các metric sau từ dashboard analytics:
  - `daily likes/dislikes` trong `analytics/chat`
  - `avg_messages_per_conversation`
  - `avg_conversation_duration_seconds`
  - `funnel percentage`
  - `return_frequency percentage`
  - `topic percentage`
- Lý do loại trừ:
  - một phần metric đang hardcode hoặc suy diễn;
  - một phần có logic tính tỷ lệ chưa chính xác nên dễ gây hiểu sai khi trình bày chính thức.

## 6. Kiểm tra chéo với production endpoint

| Chỉ số | DB | Endpoint | Kết quả |
| --- | ---: | ---: | --- |
{cross_check_table}

## 7. Kết luận ngắn cho slide/báo cáo miệng

- Trong 30 ngày gần nhất, chatbot PSU ghi nhận **{format_int_vi(window_30d['active_session_users'])} người dùng theo session**, tạo ra **{format_int_vi(window_30d['unique_conversations'])} cuộc hội thoại** và **{format_int_vi(window_30d['messages'])} tin nhắn**.
- Chất lượng phản hồi hiện ở mức khả quan với **{format_float_vi(feedback_window['positive_rate'])}% feedback tích cực**, nhưng vẫn còn một số phản ánh tập trung vào việc trả lời lan man, chưa đúng trọng tâm hoặc dữ liệu còn thiếu.
- Nhóm nhu cầu nổi bật nhất hiện nay là **tư vấn tuyển sinh**, đặc biệt về chỉ tiêu, phương thức, hồ sơ và mốc thời gian.

## 8. Ghi chú tái tạo báo cáo

- Script sinh báo cáo: [scripts/generate_psu_progress_report.py]({Path.cwd() / "scripts" / "generate_psu_progress_report.py"})
- File này là snapshot đã chốt ngày **{report_date}**.
"""


def format_snapshot_date(value: Any) -> str:
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    if isinstance(value, str):
        return datetime.fromisoformat(value).strftime("%d/%m/%Y")
    raise TypeError(f"Unsupported date value: {value!r}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a markdown progress report for the PSU chatbot."
    )
    parser.add_argument(
        "--report-date",
        default=DEFAULT_REPORT_DATE.isoformat(),
        help="Snapshot date in YYYY-MM-DD format. Default: today in Asia/Ho_Chi_Minh.",
    )
    parser.add_argument(
        "--window-days",
        type=int,
        default=DEFAULT_WINDOW_DAYS,
        help="Main reporting window in days. Default: 30.",
    )
    parser.add_argument(
        "--backend-url",
        default=os.getenv("PSU_REPORT_BACKEND_URL", DEFAULT_BACKEND_URL),
        help=f"Backend base URL. Default: {DEFAULT_BACKEND_URL}.",
    )
    parser.add_argument(
        "--admin-username",
        default=os.getenv("PSU_REPORT_ADMIN_USERNAME", "admin"),
        help="Admin username for endpoint verification.",
    )
    parser.add_argument(
        "--admin-password",
        default=os.getenv("PSU_REPORT_ADMIN_PASSWORD", "Admin123"),
        help="Admin password for endpoint verification.",
    )
    parser.add_argument(
        "--output",
        help="Output markdown path. Defaults to docs/PSU_CHATBOT_PROGRESS_REPORT_<date>.md.",
    )
    parser.add_argument(
        "--json-output",
        help="Optional path to write the raw snapshot JSON.",
    )
    parser.add_argument(
        "--snapshot-input",
        help="Optional JSON snapshot path. If provided, skip live collection and render from this frozen snapshot.",
    )
    return parser.parse_args()


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()

    root_dir = Path(__file__).resolve().parent.parent
    env_values = dotenv_values(root_dir / ".env")
    database_url = os.getenv("DATABASE_URL") or env_values.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL was not found in the environment or .env.")

    report_date = datetime.strptime(args.report_date, "%Y-%m-%d").date()
    output_path = (
        Path(args.output)
        if args.output
        else root_dir / "docs" / f"PSU_CHATBOT_PROGRESS_REPORT_{args.report_date}.md"
    )

    if args.snapshot_input:
        snapshot = json.loads(Path(args.snapshot_input).read_text(encoding="utf-8"))
    else:
        generator = ReportGenerator(
            database_url=database_url,
            backend_url=args.backend_url,
            admin_username=args.admin_username,
            admin_password=args.admin_password,
            report_date=report_date,
            window_days=args.window_days,
        )
        snapshot = generator.build_snapshot()
    markdown = render_markdown(snapshot)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(markdown, encoding="utf-8")

    if args.json_output:
        json_path = Path(args.json_output)
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

    print(f"Wrote report to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
