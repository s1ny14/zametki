# notebook/commands.py
import argparse
from .models import Note
from .storage import Storage


def add_note(args, storage: Storage):
    note = Note(title=args.title, content=args.content, priority=args.priority, status=args.status)
    if storage.save(note):
        print(f"Заметка добавлена с ID: {note.id}")
    else:
        print("Ошибка при сохранении заметки.")


def list_notes(args, storage: Storage):
    notes = storage.get_all()

    if args.priority:
        notes = [n for n in notes if n.priority == args.priority.lower()]
    if args.status:
        notes = [n for n in notes if n.status == args.status.lower()]
    if args.date:
        notes = [n for n in notes if args.date in n.created_at]

    if not notes:
        print("Нет заметок по заданным критериям.")
        return

    for note in notes:
        print(f"[{note.id}] {note.title} | {note.priority} | {note.status} | {note.created_at[:10]}")