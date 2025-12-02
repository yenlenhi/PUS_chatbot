"""
Feedback Service for managing user feedback and evaluation metrics
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy import text
from src.services.postgres_database_service import PostgresDatabaseService
from src.models.feedback import (
    FeedbackRequest,
    FeedbackResponse,
    FeedbackRecord,
    FeedbackStats,
    FeedbackTimeStats,
    ChunkPerformance,
    DashboardMetrics,
    FeedbackRating,
)
from src.utils.logger import log


class FeedbackService:
    """Service for managing user feedback and evaluation"""

    def __init__(self, db_service: PostgresDatabaseService = None):
        """
        Initialize feedback service

        Args:
            db_service: PostgreSQL database service instance
        """
        self.db_service = db_service or PostgresDatabaseService()
        self._init_feedback_tables()

    def _init_feedback_tables(self):
        """Create feedback-related tables if they don't exist"""
        try:
            with self.db_service.engine.connect() as conn:
                # Create feedback table
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS feedback (
                        id SERIAL PRIMARY KEY,
                        conversation_id VARCHAR(255) NOT NULL,
                        message_id VARCHAR(255),
                        query TEXT NOT NULL,
                        answer TEXT NOT NULL,
                        rating VARCHAR(20) NOT NULL,
                        comment TEXT,
                        chunk_ids INTEGER[] DEFAULT '{}',
                        user_id VARCHAR(255),
                        session_id VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create chunk_performance table for tracking chunk effectiveness
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS chunk_performance (
                        id SERIAL PRIMARY KEY,
                        chunk_id INTEGER NOT NULL REFERENCES chunks(id),
                        times_used INTEGER DEFAULT 0,
                        positive_feedback INTEGER DEFAULT 0,
                        negative_feedback INTEGER DEFAULT 0,
                        neutral_feedback INTEGER DEFAULT 0,
                        effectiveness_score FLOAT DEFAULT 0.5,
                        retrieval_weight FLOAT DEFAULT 1.0,
                        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(chunk_id)
                    )
                """
                    )
                )

                # Create query_metrics table for tracking query performance
                conn.execute(
                    text(
                        """
                    CREATE TABLE IF NOT EXISTS query_metrics (
                        id SERIAL PRIMARY KEY,
                        query TEXT NOT NULL,
                        response_time_ms FLOAT,
                        chunks_retrieved INTEGER,
                        confidence_score FLOAT,
                        has_feedback BOOLEAN DEFAULT FALSE,
                        feedback_id INTEGER REFERENCES feedback(id),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """
                    )
                )

                # Create indexes
                conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_feedback_conversation 
                    ON feedback(conversation_id)
                """
                    )
                )
                conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_feedback_rating 
                    ON feedback(rating)
                """
                    )
                )
                conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_feedback_created 
                    ON feedback(created_at)
                """
                    )
                )
                conn.execute(
                    text(
                        """
                    CREATE INDEX IF NOT EXISTS idx_chunk_performance_chunk 
                    ON chunk_performance(chunk_id)
                """
                    )
                )

                conn.commit()
                log.info("✅ Feedback tables initialized successfully")

        except Exception as e:
            log.error(f"❌ Error initializing feedback tables: {e}")
            raise

    def submit_feedback(self, feedback: FeedbackRequest) -> FeedbackResponse:
        """
        Submit user feedback

        Args:
            feedback: Feedback request data

        Returns:
            FeedbackResponse with submission status
        """
        try:
            session = self.db_service.SessionLocal()

            # Insert feedback record
            result = session.execute(
                text(
                    """
                    INSERT INTO feedback (
                        conversation_id, message_id, query, answer, 
                        rating, comment, chunk_ids, user_id, session_id
                    )
                    VALUES (
                        :conversation_id, :message_id, :query, :answer,
                        :rating, :comment, :chunk_ids, :user_id, :session_id
                    )
                    RETURNING id
                """
                ),
                {
                    "conversation_id": feedback.conversation_id,
                    "message_id": feedback.message_id,
                    "query": feedback.query,
                    "answer": feedback.answer,
                    "rating": feedback.rating.value,
                    "comment": feedback.comment,
                    "chunk_ids": feedback.chunk_ids or [],
                    "user_id": feedback.user_id,
                    "session_id": feedback.session_id,
                },
            )

            feedback_id = result.fetchone()[0]
            session.commit()

            # Update chunk performance based on feedback
            if feedback.chunk_ids:
                self._update_chunk_performance(feedback.chunk_ids, feedback.rating)

            log.info(
                f"✅ Feedback submitted: ID={feedback_id}, Rating={feedback.rating.value}"
            )

            return FeedbackResponse(
                id=feedback_id, status="success", message="Cảm ơn bạn đã gửi phản hồi!"
            )

        except Exception as e:
            log.error(f"❌ Error submitting feedback: {e}")
            session.rollback()
            raise
        finally:
            session.close()

    def _update_chunk_performance(self, chunk_ids: List[int], rating: FeedbackRating):
        """
        Update chunk performance metrics based on feedback

        Args:
            chunk_ids: List of chunk IDs used in the answer
            rating: User rating
        """
        try:
            session = self.db_service.SessionLocal()

            for chunk_id in chunk_ids:
                # Upsert chunk performance record
                if rating == FeedbackRating.POSITIVE:
                    session.execute(
                        text(
                            """
                        INSERT INTO chunk_performance (chunk_id, times_used, positive_feedback)
                        VALUES (:chunk_id, 1, 1)
                        ON CONFLICT (chunk_id) 
                        DO UPDATE SET 
                            times_used = chunk_performance.times_used + 1,
                            positive_feedback = chunk_performance.positive_feedback + 1,
                            last_updated = CURRENT_TIMESTAMP
                    """
                        ),
                        {"chunk_id": chunk_id},
                    )
                elif rating == FeedbackRating.NEGATIVE:
                    session.execute(
                        text(
                            """
                        INSERT INTO chunk_performance (chunk_id, times_used, negative_feedback)
                        VALUES (:chunk_id, 1, 1)
                        ON CONFLICT (chunk_id) 
                        DO UPDATE SET 
                            times_used = chunk_performance.times_used + 1,
                            negative_feedback = chunk_performance.negative_feedback + 1,
                            last_updated = CURRENT_TIMESTAMP
                    """
                        ),
                        {"chunk_id": chunk_id},
                    )
                else:
                    session.execute(
                        text(
                            """
                        INSERT INTO chunk_performance (chunk_id, times_used, neutral_feedback)
                        VALUES (:chunk_id, 1, 1)
                        ON CONFLICT (chunk_id) 
                        DO UPDATE SET 
                            times_used = chunk_performance.times_used + 1,
                            neutral_feedback = chunk_performance.neutral_feedback + 1,
                            last_updated = CURRENT_TIMESTAMP
                    """
                        ),
                        {"chunk_id": chunk_id},
                    )

                # Update effectiveness score
                self._recalculate_chunk_effectiveness(session, chunk_id)

            session.commit()

        except Exception as e:
            log.error(f"❌ Error updating chunk performance: {e}")
            session.rollback()
        finally:
            session.close()

    def _recalculate_chunk_effectiveness(self, session, chunk_id: int):
        """
        Recalculate chunk effectiveness score based on feedback history

        Score formula: (positive * 1.0 + neutral * 0.5) / total_feedback
        With a weight adjustment for retrieval ranking
        """
        try:
            result = session.execute(
                text(
                    """
                SELECT positive_feedback, negative_feedback, neutral_feedback, times_used
                FROM chunk_performance
                WHERE chunk_id = :chunk_id
            """
                ),
                {"chunk_id": chunk_id},
            )

            row = result.fetchone()
            if row:
                positive, negative, neutral, times_used = row
                total = positive + negative + neutral

                if total > 0:
                    # Calculate effectiveness score (0-1)
                    effectiveness = (positive * 1.0 + neutral * 0.5) / total

                    # Calculate retrieval weight adjustment
                    # Positive feedback increases weight, negative decreases
                    base_weight = 1.0
                    weight_adjustment = (positive - negative) * 0.1
                    retrieval_weight = max(
                        0.1, min(2.0, base_weight + weight_adjustment)
                    )

                    session.execute(
                        text(
                            """
                        UPDATE chunk_performance
                        SET effectiveness_score = :effectiveness,
                            retrieval_weight = :weight
                        WHERE chunk_id = :chunk_id
                    """
                        ),
                        {
                            "effectiveness": effectiveness,
                            "weight": retrieval_weight,
                            "chunk_id": chunk_id,
                        },
                    )

        except Exception as e:
            log.error(f"❌ Error recalculating chunk effectiveness: {e}")

    def get_feedback_stats(self, days: int = 30) -> FeedbackStats:
        """
        Get overall feedback statistics

        Args:
            days: Number of days to look back

        Returns:
            FeedbackStats with aggregated metrics
        """
        try:
            session = self.db_service.SessionLocal()

            cutoff_date = datetime.now() - timedelta(days=days)

            result = session.execute(
                text(
                    """
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN rating = 'positive' THEN 1 END) as positive,
                    COUNT(CASE WHEN rating = 'negative' THEN 1 END) as negative,
                    COUNT(CASE WHEN rating = 'neutral' THEN 1 END) as neutral
                FROM feedback
                WHERE created_at >= :cutoff_date
            """
                ),
                {"cutoff_date": cutoff_date},
            )

            row = result.fetchone()
            total = row[0] or 0
            positive = row[1] or 0
            negative = row[2] or 0
            neutral = row[3] or 0

            positive_rate = (positive / total * 100) if total > 0 else 0
            negative_rate = (negative / total * 100) if total > 0 else 0
            avg_quality = (positive * 1.0 + neutral * 0.5) / total if total > 0 else 0

            return FeedbackStats(
                total_feedback=total,
                positive_count=positive,
                negative_count=negative,
                neutral_count=neutral,
                positive_rate=round(positive_rate, 2),
                negative_rate=round(negative_rate, 2),
                avg_response_quality=round(avg_quality, 2),
            )

        except Exception as e:
            log.error(f"❌ Error getting feedback stats: {e}")
            raise
        finally:
            session.close()

    def get_daily_stats(self, days: int = 7) -> List[FeedbackTimeStats]:
        """
        Get daily feedback statistics

        Args:
            days: Number of days to look back

        Returns:
            List of daily statistics
        """
        try:
            session = self.db_service.SessionLocal()

            result = session.execute(
                text(
                    """
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as total,
                    COUNT(CASE WHEN rating = 'positive' THEN 1 END) as positive,
                    COUNT(CASE WHEN rating = 'negative' THEN 1 END) as negative,
                    COUNT(CASE WHEN rating = 'neutral' THEN 1 END) as neutral
                FROM feedback
                WHERE created_at >= CURRENT_DATE - :days
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """
                ),
                {"days": days},
            )

            stats = []
            for row in result.fetchall():
                stats.append(
                    FeedbackTimeStats(
                        date=str(row[0]),
                        total=row[1],
                        positive=row[2],
                        negative=row[3],
                        neutral=row[4],
                    )
                )

            return stats

        except Exception as e:
            log.error(f"❌ Error getting daily stats: {e}")
            raise
        finally:
            session.close()

    def get_chunk_performance(
        self, top_n: int = 10, worst: bool = False
    ) -> List[ChunkPerformance]:
        """
        Get top or worst performing chunks

        Args:
            top_n: Number of chunks to return
            worst: If True, return worst performing chunks

        Returns:
            List of chunk performance metrics
        """
        try:
            session = self.db_service.SessionLocal()

            order = "ASC" if worst else "DESC"

            result = session.execute(
                text(
                    f"""
                SELECT 
                    cp.chunk_id,
                    c.source_file,
                    cp.times_used,
                    cp.positive_feedback,
                    cp.negative_feedback,
                    cp.effectiveness_score
                FROM chunk_performance cp
                JOIN chunks c ON cp.chunk_id = c.id
                WHERE cp.times_used >= 3
                ORDER BY cp.effectiveness_score {order}
                LIMIT :limit
            """
                ),
                {"limit": top_n},
            )

            chunks = []
            for row in result.fetchall():
                chunks.append(
                    ChunkPerformance(
                        chunk_id=row[0],
                        source_file=row[1],
                        times_used=row[2],
                        positive_feedback=row[3],
                        negative_feedback=row[4],
                        effectiveness_score=round(row[5], 2),
                    )
                )

            return chunks

        except Exception as e:
            log.error(f"❌ Error getting chunk performance: {e}")
            raise
        finally:
            session.close()

    def get_retrieval_weights(self) -> Dict[int, float]:
        """
        Get current retrieval weights for all chunks with feedback

        Returns:
            Dictionary mapping chunk_id to retrieval_weight
        """
        try:
            session = self.db_service.SessionLocal()

            result = session.execute(
                text(
                    """
                SELECT chunk_id, retrieval_weight
                FROM chunk_performance
                WHERE times_used >= 1
            """
                )
            )

            weights = {}
            for row in result.fetchall():
                weights[row[0]] = row[1]

            return weights

        except Exception as e:
            log.error(f"❌ Error getting retrieval weights: {e}")
            return {}
        finally:
            session.close()

    def get_recent_negative_feedback(self, limit: int = 10) -> List[FeedbackRecord]:
        """
        Get recent negative feedback for review

        Args:
            limit: Maximum number of records to return

        Returns:
            List of recent negative feedback records
        """
        try:
            session = self.db_service.SessionLocal()

            result = session.execute(
                text(
                    """
                SELECT 
                    id, conversation_id, message_id, query, answer,
                    rating, comment, chunk_ids, user_id, session_id, created_at
                FROM feedback
                WHERE rating = 'negative'
                ORDER BY created_at DESC
                LIMIT :limit
            """
                ),
                {"limit": limit},
            )

            records = []
            for row in result.fetchall():
                records.append(
                    FeedbackRecord(
                        id=row[0],
                        conversation_id=row[1],
                        message_id=row[2],
                        query=row[3],
                        answer=row[4],
                        rating=FeedbackRating(row[5]),
                        comment=row[6],
                        chunk_ids=row[7] or [],
                        user_id=row[8],
                        session_id=row[9],
                        created_at=row[10],
                    )
                )

            return records

        except Exception as e:
            log.error(f"❌ Error getting recent negative feedback: {e}")
            raise
        finally:
            session.close()

    def get_dashboard_metrics(self) -> DashboardMetrics:
        """
        Get comprehensive dashboard metrics

        Returns:
            DashboardMetrics with all monitoring data
        """
        try:
            session = self.db_service.SessionLocal()

            # Get overall stats
            overall_stats = self.get_feedback_stats(days=30)

            # Get daily stats
            daily_stats = self.get_daily_stats(days=7)

            # Get query metrics
            result = session.execute(
                text(
                    """
                SELECT 
                    AVG(response_time_ms) as avg_time,
                    COUNT(*) as total_queries,
                    COUNT(CASE WHEN has_feedback THEN 1 END) as queries_with_feedback
                FROM query_metrics
                WHERE created_at >= CURRENT_DATE - 30
            """
                )
            )

            row = result.fetchone()
            avg_response_time = row[0] or 0
            total_queries = row[1] or 0
            queries_with_feedback = row[2] or 0
            feedback_rate = (
                (queries_with_feedback / total_queries * 100)
                if total_queries > 0
                else 0
            )

            # Get top and worst chunks
            top_chunks = self.get_chunk_performance(top_n=5, worst=False)
            worst_chunks = self.get_chunk_performance(top_n=5, worst=True)

            # Get recent negative feedback
            recent_negative = self.get_recent_negative_feedback(limit=5)

            return DashboardMetrics(
                overall_stats=overall_stats,
                daily_stats=daily_stats,
                avg_response_time_ms=round(avg_response_time, 2),
                total_queries=total_queries,
                queries_with_feedback=queries_with_feedback,
                feedback_rate=round(feedback_rate, 2),
                top_chunks=top_chunks,
                worst_chunks=worst_chunks,
                recent_negative_feedback=recent_negative,
            )

        except Exception as e:
            log.error(f"❌ Error getting dashboard metrics: {e}")
            raise
        finally:
            session.close()

    def record_query_metrics(
        self,
        query: str,
        response_time_ms: float,
        chunks_retrieved: int,
        confidence_score: float,
    ) -> int:
        """
        Record query metrics for monitoring

        Args:
            query: The user's query
            response_time_ms: Response time in milliseconds
            chunks_retrieved: Number of chunks retrieved
            confidence_score: Confidence score of the response

        Returns:
            Query metrics record ID
        """
        try:
            session = self.db_service.SessionLocal()

            result = session.execute(
                text(
                    """
                INSERT INTO query_metrics (query, response_time_ms, chunks_retrieved, confidence_score)
                VALUES (:query, :response_time, :chunks, :confidence)
                RETURNING id
            """
                ),
                {
                    "query": query,
                    "response_time": response_time_ms,
                    "chunks": chunks_retrieved,
                    "confidence": confidence_score,
                },
            )

            metric_id = result.fetchone()[0]
            session.commit()

            return metric_id

        except Exception as e:
            log.error(f"❌ Error recording query metrics: {e}")
            session.rollback()
            return -1
        finally:
            session.close()

    def link_feedback_to_query(self, feedback_id: int, query_metric_id: int):
        """
        Link feedback to query metrics

        Args:
            feedback_id: Feedback record ID
            query_metric_id: Query metrics record ID
        """
        try:
            session = self.db_service.SessionLocal()

            session.execute(
                text(
                    """
                UPDATE query_metrics
                SET has_feedback = TRUE, feedback_id = :feedback_id
                WHERE id = :query_id
            """
                ),
                {"feedback_id": feedback_id, "query_id": query_metric_id},
            )

            session.commit()

        except Exception as e:
            log.error(f"❌ Error linking feedback to query: {e}")
            session.rollback()
        finally:
            session.close()

    def get_feedback_for_training(self, min_samples: int = 100) -> List[Dict[str, Any]]:
        """
        Get feedback data for potential fine-tuning

        Args:
            min_samples: Minimum number of samples required

        Returns:
            List of training data samples
        """
        try:
            session = self.db_service.SessionLocal()

            result = session.execute(
                text(
                    """
                SELECT query, answer, rating, chunk_ids
                FROM feedback
                WHERE rating != 'neutral'
                ORDER BY created_at DESC
                LIMIT 1000
            """
                )
            )

            samples = []
            for row in result.fetchall():
                samples.append(
                    {
                        "query": row[0],
                        "answer": row[1],
                        "label": 1 if row[2] == "positive" else 0,
                        "chunk_ids": row[3],
                    }
                )

            if len(samples) < min_samples:
                log.warning(
                    f"⚠️ Only {len(samples)} samples available, need {min_samples} for training"
                )

            return samples

        except Exception as e:
            log.error(f"❌ Error getting training data: {e}")
            return []
        finally:
            session.close()

    def export_feedback_report(self, days: int = 30) -> Dict[str, Any]:
        """
        Export comprehensive feedback report

        Args:
            days: Number of days to include in report

        Returns:
            Dictionary with report data
        """
        try:
            dashboard = self.get_dashboard_metrics()
            training_data = self.get_feedback_for_training()
            weights = self.get_retrieval_weights()

            return {
                "report_date": datetime.now().isoformat(),
                "period_days": days,
                "summary": {
                    "total_feedback": dashboard.overall_stats.total_feedback,
                    "positive_rate": dashboard.overall_stats.positive_rate,
                    "negative_rate": dashboard.overall_stats.negative_rate,
                    "avg_response_quality": dashboard.overall_stats.avg_response_quality,
                    "feedback_rate": dashboard.feedback_rate,
                },
                "daily_breakdown": [
                    stat.model_dump() for stat in dashboard.daily_stats
                ],
                "top_performing_chunks": [
                    chunk.model_dump() for chunk in dashboard.top_chunks
                ],
                "worst_performing_chunks": [
                    chunk.model_dump() for chunk in dashboard.worst_chunks
                ],
                "retrieval_weights_updated": len(weights),
                "training_samples_available": len(training_data),
                "recommendations": self._generate_recommendations(dashboard),
            }

        except Exception as e:
            log.error(f"❌ Error exporting feedback report: {e}")
            raise

    def _generate_recommendations(self, dashboard: DashboardMetrics) -> List[str]:
        """Generate improvement recommendations based on metrics"""
        recommendations = []

        if dashboard.overall_stats.negative_rate > 20:
            recommendations.append(
                "⚠️ High negative feedback rate detected. Review recent negative feedback for patterns."
            )

        if dashboard.feedback_rate < 10:
            recommendations.append(
                "💡 Low feedback rate. Consider adding more prominent feedback prompts."
            )

        if dashboard.worst_chunks:
            chunk_ids = [c.chunk_id for c in dashboard.worst_chunks[:3]]
            recommendations.append(
                f"📝 Consider reviewing/improving chunks: {chunk_ids}"
            )

        if len(self.get_feedback_for_training()) >= 100:
            recommendations.append(
                "🎯 Sufficient data for fine-tuning. Consider training custom embeddings."
            )

        return recommendations
