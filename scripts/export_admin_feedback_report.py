#!/usr/bin/env python
"""Export PSU feedback report from admin APIs and render markdown snapshot."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_BASE_URL = "https://puschatbot-production.up.railway.app"
DEFAULT_DAYS = 30


def format_int_vi(value: int) -> str:
    return f"{value:,}".replace(",", ".")


def format_float_vi(value: float, digits: int = 2) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def short_text(text: str | None, limit: int = 140) -> str:
    if not text:
        return ""
    normalized = " ".join(str(text).split())
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3].rstrip() + "..."


def load_env_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#") or "=" not in cleaned:
            continue
        key, value = cleaned.split("=", 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def http_json(
    url: str,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    payload: dict[str, Any] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    data = None
    req_headers = headers.copy() if headers else {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        req_headers.setdefault("Content-Type", "application/json")

    req = request.Request(url=url, method=method, headers=req_headers, data=data)
    with request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def login(base_url: str, username: str, password: str) -> str:
    payload = {"username": username, "password": password}
    data = http_json(f"{base_url}/api/v1/auth/login", method="POST", payload=payload)
    token = data.get("access_token")
    if not token:
        raise RuntimeError("Login succeeded but no access_token was returned.")
    return str(token)


def build_markdown(snapshot: dict[str, Any]) -> str:
    md = snapshot["metadata"]
    ep = snapshot["endpoints"]

    stats_30d = ep["feedback_stats_30d"]
    stats_all = ep["feedback_stats_all_time"]
    traffic = ep["traffic_summary"]
    chat = ep["chat_overview"]
    daily = ep["feedback_daily"]
    recent_negative = ep["feedback_recent_negative"]
    export_data = ep["feedback_export"]

    report_date = datetime.fromisoformat(md["report_date"]).strftime("%d/%m/%Y")
    period_days = int(md["period_days"])
    period_start = datetime.fromisoformat(md["period_start"]).strftime("%d/%m/%Y")
    period_end = datetime.fromisoformat(md["period_end"]).strftime("%d/%m/%Y")

    negative_records = recent_negative.get("records", []) or []
    negative_lines = "\n".join(
        f"- `{str(item.get('created_at', ''))[:10]}` | {short_text(item.get('query'), 120)} | phản hồi: \"{short_text(item.get('comment'), 140)}\""
        for item in negative_records[:5]
    )
    if not negative_lines:
        negative_lines = "- Không có phản hồi tiêu cực gần đây."

    daily_stats = daily.get("daily_stats", []) or []
    daily_avg_total = (
        sum(int(row.get("total", 0)) for row in daily_stats) / len(daily_stats)
        if daily_stats
        else 0.0
    )

    recommendations = export_data.get("recommendations", []) or []
    recommendation_lines = "\n".join(
        f"- {short_text(item, 180)}" for item in recommendations
    )
    if not recommendation_lines:
        recommendation_lines = "- Không có khuyến nghị tự động tại thời điểm export."

    return f"""# Báo cáo tiến độ chatbot PSU

**Mốc chốt số liệu:** {report_date}  
**Khoảng vận hành chính:** {period_days} ngày gần nhất ({period_start} đến {period_end})  
**Nguồn chính:** Admin API production (`/api/v1/feedback/*`, `/api/v1/admin/chat-history/*`, `/api/v1/analytics/*`)  
**Nguồn đối chiếu:** Endpoint export feedback (`/api/v1/feedback/export?days={period_days}`)

## 1. Tóm tắt điều hành

- Chatbot ghi nhận **{format_int_vi(int(stats_30d.get('total_feedback', 0)))} feedback trong {period_days} ngày**, với **{format_float_vi(float(stats_30d.get('positive_rate', 0.0)))}% tích cực**.
- Tổng cộng toàn thời gian hiện có **{format_int_vi(int(stats_all.get('total_feedback', 0)))} feedback**, trong đó **{format_int_vi(int(stats_all.get('positive_count', 0)))} tích cực** và **{format_int_vi(int(stats_all.get('negative_count', 0)))} tiêu cực**.
- Hệ thống conversation hiện có **{format_int_vi(int(chat.get('total_conversations', 0)))} conversation** và **{format_int_vi(int(chat.get('total_messages', 0)))} tin nhắn** toàn thời gian.
- Lưu lượng web hiện tại: **{format_int_vi(int(traffic.get('online_now', 0)))} online**, **{format_int_vi(int(traffic.get('total_views', 0)))} page views** toàn thời gian.

## 2. Số liệu chính

### 2.1. Tình trạng public hiện tại

- **{format_int_vi(int(traffic.get('online_now', 0)))}** người online tại thời điểm kiểm tra.
- **{format_int_vi(int(traffic.get('total_views', 0)))}** page views toàn thời gian.
- **{format_int_vi(int(traffic.get('month_views', 0)))}** lượt xem trong tháng hiện tại.

### 2.2. Vận hành hội thoại

- **{format_int_vi(int(chat.get('total_conversations', 0)))}** conversation toàn thời gian.
- **{format_int_vi(int(chat.get('total_messages', 0)))}** tin nhắn toàn thời gian.
- **{format_int_vi(int(chat.get('today_conversations', 0)))}** conversation phát sinh hôm nay.
- **{format_int_vi(int(chat.get('active_conversations', 0)))}** conversation đang active.

## 3. Phản hồi người dùng

### 3.1. Thống kê phản hồi

- **{period_days} ngày gần nhất:** {format_int_vi(int(stats_30d.get('total_feedback', 0)))} feedback gồm {format_int_vi(int(stats_30d.get('positive_count', 0)))} tích cực, {format_int_vi(int(stats_30d.get('negative_count', 0)))} tiêu cực, {format_int_vi(int(stats_30d.get('neutral_count', 0)))} trung tính.
- **Tỷ lệ {period_days} ngày:** tích cực **{format_float_vi(float(stats_30d.get('positive_rate', 0.0)))}%**, tiêu cực **{format_float_vi(float(stats_30d.get('negative_rate', 0.0)))}%**.
- **Toàn thời gian:** {format_int_vi(int(stats_all.get('total_feedback', 0)))} feedback gồm {format_int_vi(int(stats_all.get('positive_count', 0)))} tích cực, {format_int_vi(int(stats_all.get('negative_count', 0)))} tiêu cực, {format_int_vi(int(stats_all.get('neutral_count', 0)))} trung tính.

### 3.2. Nhịp feedback theo ngày

- Số ngày có dữ liệu feedback trong kỳ: **{format_int_vi(len(daily_stats))}** ngày.
- Trung bình feedback/ngày trong kỳ: **{format_float_vi(daily_avg_total)}**.

### 3.3. Các phản hồi tiêu cực gần đây

{negative_lines}

## 4. Kiểm tra chéo với endpoint export feedback

- Tổng feedback kỳ báo cáo (`feedback/stats`) và (`feedback/export`) đều là **{format_int_vi(int(stats_30d.get('total_feedback', 0)))}**.
- Tỷ lệ tích cực kỳ báo cáo từ endpoint thống kê là **{format_float_vi(float(stats_30d.get('positive_rate', 0.0)))}%**.
- Chỉ số chất lượng trung bình phản hồi (`avg_response_quality`) là **{format_float_vi(float(stats_30d.get('avg_response_quality', 0.0)))}**.

## 5. Khuyến nghị tự động từ hệ thống

{recommendation_lines}

## 6. Ghi chú tái tạo báo cáo

- Script export: [scripts/export_admin_feedback_report.py](scripts/export_admin_feedback_report.py)
- Đây là snapshot được export tự động ngày **{report_date}** từ trang admin feedback/API production.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export PSU feedback report from admin APIs."
    )
    parser.add_argument("--report-date", default=datetime.now().date().isoformat())
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS)
    parser.add_argument(
        "--base-url", default=os.getenv("PSU_REPORT_BACKEND_URL", DEFAULT_BASE_URL)
    )
    parser.add_argument(
        "--admin-username", default=os.getenv("PSU_REPORT_ADMIN_USERNAME", "admin")
    )
    parser.add_argument(
        "--admin-password", default=os.getenv("PSU_REPORT_ADMIN_PASSWORD", "Admin123")
    )
    parser.add_argument("--output")
    parser.add_argument("--json-output")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent.parent
    env_values = load_env_file(root / ".env")

    base_url = (env_values.get("PSU_REPORT_BACKEND_URL") or args.base_url).rstrip("/")
    admin_username = env_values.get("PSU_REPORT_ADMIN_USERNAME") or args.admin_username
    admin_password = env_values.get("PSU_REPORT_ADMIN_PASSWORD") or args.admin_password

    report_day = datetime.strptime(args.report_date, "%Y-%m-%d")
    period_end = report_day.replace(hour=23, minute=59, second=59)
    period_start = (period_end - timedelta(days=args.days - 1)).replace(
        hour=0,
        minute=0,
        second=0,
    )

    output_md = (
        Path(args.output)
        if args.output
        else root / "docs" / f"PSU_CHATBOT_PROGRESS_REPORT_{args.report_date}.md"
    )
    output_json = (
        Path(args.json_output)
        if args.json_output
        else root / "artifacts" / f"psu_progress_report_{args.report_date}.json"
    )

    try:
        token = login(base_url, admin_username, admin_password)
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"Login failed ({exc.code}): {body}") from exc

    auth_headers = {"Authorization": f"Bearer {token}"}

    endpoints = {
        "feedback_stats_30d": http_json(
            f"{base_url}/api/v1/feedback/stats?days={args.days}", headers=auth_headers
        ),
        "feedback_stats_all_time": http_json(
            f"{base_url}/api/v1/feedback/stats?days=3650", headers=auth_headers
        ),
        "feedback_recent_negative": http_json(
            f"{base_url}/api/v1/feedback/negative/recent?limit=5", headers=auth_headers
        ),
        "feedback_daily": http_json(
            f"{base_url}/api/v1/feedback/daily?days={args.days}", headers=auth_headers
        ),
        "feedback_export": http_json(
            f"{base_url}/api/v1/feedback/export?days={args.days}", headers=auth_headers
        ),
        "chat_overview": http_json(
            f"{base_url}/api/v1/admin/chat-history/stats/overview", headers=auth_headers
        ),
        "traffic_summary": http_json(
            f"{base_url}/api/v1/analytics/traffic-summary", headers=auth_headers
        ),
    }

    snapshot = {
        "metadata": {
            "report_date": args.report_date,
            "generated_at": datetime.now().isoformat(),
            "period_days": args.days,
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "base_url": base_url,
        },
        "endpoints": endpoints,
    }

    markdown = build_markdown(snapshot)
    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text(markdown, encoding="utf-8")
    output_json.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Wrote markdown: {output_md}")
    print(f"Wrote json: {output_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
