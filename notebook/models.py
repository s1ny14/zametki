from datetime import datetime
from typing import Optional, List

class Note:
    def __init__(self, title: str, content: str,
                 priority: str = "medium", status: str = "active",
                 tags: List[str] = None):
        self.id: Optional[int] = None
        self.title = title.strip()
        self.content = content.strip()
        self.priority = priority.lower()
        self.status = status.lower()
        self.tags = [t.strip().lower() for t in (tags or []) if t.strip()]
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "priority": self.priority,
            "status": self.status,
            "tags": self.tags,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):
        note = Note(
            title=data["title"],
            content=data["content"],
            priority=data["priority"],
            status=data["status"],
            tags=data.get("tags", [])
        )
        note.id = data["id"]
        note.created_at = data["created_at"]
        return note