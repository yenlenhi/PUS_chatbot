"""
Upload Task Manager - Track background PDF processing tasks
"""

import uuid
from datetime import datetime
from typing import Dict, Optional
from enum import Enum
from dataclasses import dataclass
from src.utils.logger import log


class TaskStatus(str, Enum):
    """Task status enum"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class UploadTask:
    """Upload task information"""

    task_id: str
    filename: str
    original_filename: str
    status: TaskStatus
    category: str
    use_gemini: bool
    file_size: int
    created_at: datetime
    updated_at: datetime
    progress: int = 0  # 0-100
    message: str = ""
    chunks_created: int = 0
    embeddings_created: int = 0
    supabase_url: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self):
        """Convert to dict for JSON serialization"""
        data = {
            "task_id": self.task_id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "status": self.status.value,
            "progress": self.progress,
            "message": self.message,
            "category": self.category,
            "use_gemini": self.use_gemini,
            "file_size": self.file_size,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "supabase_url": self.supabase_url,
        }
        
        # Add result information
        if self.status == TaskStatus.COMPLETED:
            data["result"] = {
                "success": True,
                "chunks_created": self.chunks_created,
                "embeddings_created": self.embeddings_created,
                "status": "success",
            }
        elif self.status == TaskStatus.FAILED:
            data["result"] = {
                "success": False,
                "error": self.error,
                "status": "error",
            }
        
        return data


class UploadTaskManager:
    """Manage upload tasks in-memory (could be replaced with Redis later)"""

    def __init__(self):
        self._tasks: Dict[str, UploadTask] = {}
        log.info("📋 UploadTaskManager initialized")

    def create_task(
        self,
        filename: str,
        original_filename: str,
        category: str,
        use_gemini: bool,
        file_size: int,
        supabase_url: Optional[str] = None,
    ) -> str:
        """Create a new upload task"""
        task_id = str(uuid.uuid4())
        now = datetime.now()

        task = UploadTask(
            task_id=task_id,
            filename=filename,
            original_filename=original_filename,
            status=TaskStatus.PENDING,
            category=category,
            use_gemini=use_gemini,
            file_size=file_size,
            created_at=now,
            updated_at=now,
            progress=0,
            message="File uploaded, waiting to process...",
            supabase_url=supabase_url,
        )

        self._tasks[task_id] = task
        log.info(f"📋 Created task {task_id} for file: {original_filename}")
        return task_id

    def get_task(self, task_id: str) -> Optional[UploadTask]:
        """Get task by ID"""
        return self._tasks.get(task_id)

    def update_task(
        self,
        task_id: str,
        status: Optional[TaskStatus] = None,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        chunks_created: Optional[int] = None,
        embeddings_created: Optional[int] = None,
        error: Optional[str] = None,
    ):
        """Update task information"""
        task = self._tasks.get(task_id)
        if not task:
            log.warning(f"⚠️ Task {task_id} not found")
            return

        if status is not None:
            task.status = status
        if progress is not None:
            task.progress = progress
        if message is not None:
            task.message = message
        if chunks_created is not None:
            task.chunks_created = chunks_created
        if embeddings_created is not None:
            task.embeddings_created = embeddings_created
        if error is not None:
            task.error = error

        task.updated_at = datetime.now()
        log.debug(f"📋 Updated task {task_id}: {status} - {progress}% - {message}")

    def delete_task(self, task_id: str):
        """Delete task (cleanup after completion)"""
        if task_id in self._tasks:
            del self._tasks[task_id]
            log.info(f"🗑️ Deleted task {task_id}")

    def get_all_tasks(self) -> Dict[str, UploadTask]:
        """Get all tasks (for debugging)"""
        return self._tasks.copy()


# Global instance
_task_manager = None


def get_task_manager() -> UploadTaskManager:
    """Get or create task manager instance"""
    global _task_manager
    if _task_manager is None:
        _task_manager = UploadTaskManager()
    return _task_manager
