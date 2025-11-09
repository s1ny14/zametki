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

def search_notes(args, storage: Storage):
    notes = storage.get_all()
    keyword = args.keyword.lower()
    found = [n for n in notes if keyword in n.title.lower() or keyword in n.content.lower()]

    if not found:
        print("Ничего не найдено.")
        return

    for note in found:
        print(f"[{note.id}] {note.title}")
        print(f"    {note.content[:60]}{'...' if len(note.content) > 60 else ''}")
        print(f"    Приоритет: {note.priority}, Статус: {note.status}, Дата: {note.created_at[:10]}\n")

def delete_note(args, storage: Storage):
    try:
        note_id = int(args.id)
    except ValueError:
        print("ID должен быть числом.")
        return
    if storage.delete(note_id):
        print(f"Заметка с ID {note_id} удалена.")
    else:
        print(f"Заметка с ID {note_id} не найдена.")

def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Менеджер заметок")
    subparsers = parser.add_subparsers(dest="command", help="Команды")

    # add
    add_parser = subparsers.add_parser("add", help="Добавить заметку")
    add_parser.add_argument("--title", required=True, help="Заголовок")
    add_parser.add_argument("--content", required=True, help="Содержание")
    add_parser.add_argument("--priority", choices=["low", "medium", "high"], default="medium")
    add_parser.add_argument("--status", choices=["active", "done", "archived"], default="active")

    # list
    list_parser = subparsers.add_parser("list", help="Список заметок")
    list_parser.add_argument("--priority", choices=["low", "medium", "high"])
    list_parser.add_argument("--status", choices=["active", "done", "archived"])
    list_parser.add_argument("--date", help="Фильтр по дате (YYYY-MM-DD)")

    # search
    search_parser = subparsers.add_parser("search", help="Поиск")
    search_parser.add_argument("--keyword", required=True, help="Ключевое слово")

    # delete
    delete_parser = subparsers.add_parser("delete", help="Удалить")
    delete_parser.add_argument("--id", required=True, help="ID заметки")

    return parser