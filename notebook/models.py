from datetime import datetime
from typing import Optional

class Note:
    def __init__(self, title: str, content: str, priority: str = "medium", status: str = "active"):
        self.id: Optional[int] = None
        self.title = title.strip()
        self.content = content.strip()
        self.priority = priority.lower()
        self.status = status.lower()
        self.created_at = datetime.now().isoformat()

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at
        }

    @staticmethod
    def from_dict(data):
        note = Note(data["title"], data["content"], data["priority"], data["status"])
        note.id = data["id"]
        note.created_at = data["created_at"]
        return note