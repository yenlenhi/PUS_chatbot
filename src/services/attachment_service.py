"""
Service for managing document attachments (forms, templates, etc.)
"""

from typing import List, Optional
from sqlalchemy import text
from pathlib import Path
from src.utils.logger import log
from src.services.postgres_database_service import PostgresDatabaseService
from src.models.schemas import DocumentAttachment


class AttachmentService:
    """Service for managing document attachments"""

    def __init__(self, db_service: PostgresDatabaseService):
        """Initialize attachment service"""
        self.db = db_service
        self.forms_dir = Path("data/forms")
        self.forms_dir.mkdir(parents=True, exist_ok=True)

    def create_attachment(
        self,
        file_name: str,
        file_type: str,
        file_path: str,
        file_size: Optional[int] = None,
        description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
    ) -> int:
        """
        Create a new attachment record

        Args:
            file_name: Name of the file
            file_type: File type (doc, docx, xlsx, etc.)
            file_path: Path to the file
            file_size: File size in bytes
            description: Description of the attachment
            keywords: Keywords for searching

        Returns:
            Attachment ID
        """
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                        INSERT INTO document_attachments 
                        (file_name, file_type, file_path, file_size, description, keywords, is_active)
                        VALUES (:file_name, :file_type, :file_path, :file_size, :description, :keywords, TRUE)
                        RETURNING id
                    """
                    ),
                    {
                        "file_name": file_name,
                        "file_type": file_type,
                        "file_path": file_path,
                        "file_size": file_size,
                        "description": description,
                        "keywords": keywords or [],
                    },
                )
                conn.commit()
                attachment_id = result.fetchone()[0]
                log.info(f"✅ Created attachment: {file_name} (ID: {attachment_id})")
                return attachment_id
        except Exception as e:
            log.error(f"❌ Error creating attachment: {e}")
            raise

    def link_attachment_to_chunks(
        self, attachment_id: int, chunk_ids: List[int], relevance_score: float = 1.0
    ):
        """
        Link an attachment to multiple chunks

        Args:
            attachment_id: ID of the attachment
            chunk_ids: List of chunk IDs to link
            relevance_score: Relevance score for the link
        """
        try:
            with self.db.engine.connect() as conn:
                for chunk_id in chunk_ids:
                    conn.execute(
                        text(
                            """
                            INSERT INTO chunk_attachments (chunk_id, attachment_id, relevance_score)
                            VALUES (:chunk_id, :attachment_id, :relevance_score)
                            ON CONFLICT (chunk_id, attachment_id) DO UPDATE
                            SET relevance_score = :relevance_score
                        """
                        ),
                        {
                            "chunk_id": chunk_id,
                            "attachment_id": attachment_id,
                            "relevance_score": relevance_score,
                        },
                    )
                conn.commit()
                log.info(
                    f"✅ Linked attachment {attachment_id} to {len(chunk_ids)} chunks"
                )
        except Exception as e:
            log.error(f"❌ Error linking attachment to chunks: {e}")
            raise

    def get_attachments_by_chunk_ids(
        self, chunk_ids: List[int]
    ) -> List[DocumentAttachment]:
        """
        Get all attachments linked to given chunk IDs

        Args:
            chunk_ids: List of chunk IDs

        Returns:
            List of DocumentAttachment objects
        """
        if not chunk_ids:
            return []

        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                        SELECT DISTINCT a.id, a.file_name, a.file_type, a.file_path, 
                               a.file_size, a.description, a.keywords
                        FROM document_attachments a
                        JOIN chunk_attachments ca ON a.id = ca.attachment_id
                        WHERE ca.chunk_id = ANY(:chunk_ids) AND a.is_active = TRUE
                        ORDER BY a.id
                    """
                    ),
                    {"chunk_ids": chunk_ids},
                )

                attachments = []
                for row in result:
                    attachments.append(
                        DocumentAttachment(
                            id=row[0],
                            file_name=row[1],
                            file_type=row[2],
                            file_path=row[3],
                            file_size=row[4],
                            description=row[5],
                            keywords=row[6] if row[6] else [],
                            download_url=f"/api/v1/attachments/download/{row[0]}",
                        )
                    )
                return attachments
        except Exception as e:
            log.error(f"❌ Error getting attachments: {e}")
            return []

    def get_attachment_by_id(self, attachment_id: int) -> Optional[DocumentAttachment]:
        """
        Get an attachment by ID

        Args:
            attachment_id: ID of the attachment

        Returns:
            DocumentAttachment object or None
        """
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                        SELECT id, file_name, file_type, file_path, file_size, 
                               description, keywords
                        FROM document_attachments
                        WHERE id = :id AND is_active = TRUE
                    """
                    ),
                    {"id": attachment_id},
                )
                row = result.fetchone()
                if row:
                    return DocumentAttachment(
                        id=row[0],
                        file_name=row[1],
                        file_type=row[2],
                        file_path=row[3],
                        file_size=row[4],
                        description=row[5],
                        keywords=row[6] if row[6] else [],
                        download_url=f"/api/v1/attachments/download/{row[0]}",
                    )
                return None
        except Exception as e:
            log.error(f"❌ Error getting attachment by ID: {e}")
            return None

    def search_attachments(
        self, keywords: Optional[List[str]] = None, file_name: Optional[str] = None
    ) -> List[DocumentAttachment]:
        """
        Search attachments by keywords or file name
        Uses flexible matching: keywords overlap OR description contains keywords

        Args:
            keywords: List of keywords to search
            file_name: File name to search (partial match)

        Returns:
            List of DocumentAttachment objects
        """
        try:
            with self.db.engine.connect() as conn:
                query = """
                    SELECT id, file_name, file_type, file_path, file_size, 
                           description, keywords
                    FROM document_attachments
                    WHERE is_active = TRUE
                """
                params = {}

                if keywords:
                    # Flexible search: match if ANY keyword overlaps OR appears in description/filename
                    keyword_conditions = []
                    for i, kw in enumerate(keywords):
                        keyword_conditions.append(
                            f"(keywords && ARRAY[:kw{i}]::text[] OR "
                            f"description ILIKE :kw_desc{i} OR "
                            f"file_name ILIKE :kw_file{i})"
                        )
                        params[f"kw{i}"] = kw
                        params[f"kw_desc{i}"] = f"%{kw}%"
                        params[f"kw_file{i}"] = f"%{kw}%"

                    query += " AND (" + " OR ".join(keyword_conditions) + ")"

                if file_name:
                    query += " AND file_name ILIKE :file_name"
                    params["file_name"] = f"%{file_name}%"

                query += " ORDER BY created_at DESC"

                result = conn.execute(text(query), params)

                attachments = []
                for row in result:
                    attachments.append(
                        DocumentAttachment(
                            id=row[0],
                            file_name=row[1],
                            file_type=row[2],
                            file_path=row[3],
                            file_size=row[4],
                            description=row[5],
                            keywords=row[6] if row[6] else [],
                            download_url=f"/api/v1/attachments/download/{row[0]}",
                        )
                    )
                return attachments
        except Exception as e:
            log.error(f"❌ Error searching attachments: {e}")
            return []

    def get_all_attachments(self) -> List[DocumentAttachment]:
        """
        Get all active attachments

        Returns:
            List of DocumentAttachment objects
        """
        try:
            with self.db.engine.connect() as conn:
                result = conn.execute(
                    text(
                        """
                        SELECT id, file_name, file_type, file_path, file_size, 
                               description, keywords
                        FROM document_attachments
                        WHERE is_active = TRUE
                        ORDER BY created_at DESC
                    """
                    )
                )

                attachments = []
                for row in result:
                    attachments.append(
                        DocumentAttachment(
                            id=row[0],
                            file_name=row[1],
                            file_type=row[2],
                            file_path=row[3],
                            file_size=row[4],
                            description=row[5],
                            keywords=row[6] if row[6] else [],
                            download_url=f"/api/v1/attachments/download/{row[0]}",
                        )
                    )
                return attachments
        except Exception as e:
            log.error(f"❌ Error getting all attachments: {e}")
            return []

    def delete_attachment(self, attachment_id: int) -> bool:
        """
        Soft delete an attachment (set is_active to False)

        Args:
            attachment_id: ID of the attachment

        Returns:
            True if successful
        """
        try:
            with self.db.engine.connect() as conn:
                conn.execute(
                    text(
                        """
                        UPDATE document_attachments
                        SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP
                        WHERE id = :id
                    """
                    ),
                    {"id": attachment_id},
                )
                conn.commit()
                log.info(f"✅ Deleted attachment {attachment_id}")
                return True
        except Exception as e:
            log.error(f"❌ Error deleting attachment: {e}")
            return False
