import json
import os
from typing import List, Dict
from .models import Note

NOTES_FILE = "notes.json"

class Storage:
    def __init__(self, file_path: str = NOTES_FILE):
        self.file_path = file_path

    def _load_notes(self) -> List[Dict]:
        """Читает заметки из файла. Возвращает пустой список, если файл не существует."""
        if not os.path.exists(self.file_path):
            return []
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, PermissionError) as e:
            print(f"Ошибка при чтении файла: {e}")
            return []

    def _save_notes(self, notes: List[Dict]) -> bool:
        """Сохраняет заметки в файл."""
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(notes, f, ensure_ascii=False, indent=2)
            return True
        except (PermissionError, OSError) as e:
            print(f"Ошибка при записи в файл: {e}")
            return False

    def get_all(self) -> List[Note]:
        """Возвращает все заметки как объекты Note."""
        data = self._load_notes()
        notes = []
        for item in data:
            note = Note.from_dict(item)
            notes.append(note)
        return notes

    def save(self, note: Note) -> bool:
        """Сохраняет одну заметку (добавляет или обновляет)."""
        notes = self.get_all()
        if note.id is None:
            # Новая заметка — назначаем ID
            note.id = max([n.id for n in notes] + [0]) + 1
            notes.append(note)
        else:
            # Обновляем существующую
            notes = [n for n in notes if n.id != note.id]
            notes.append(note)
        return self._save_notes([n.to_dict() for n in notes])

    def delete(self, note_id: int) -> bool:
        """Удаляет заметку по ID."""
        notes = self.get_all()
        filtered = [n for n in notes if n.id != note_id]
        if len(filtered) == len(notes):
            return False  # Не найдено
        return self._save_notes([n.to_dict() for n in filtered])