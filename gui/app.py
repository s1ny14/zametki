# gui/app.py
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from notebook import Storage, Note

class NoteApp:
    """Главное окно приложения."""
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер заметок")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        self.storage = Storage()

        self.setup_ui()
        self.refresh_notes()

    def setup_ui(self):
        # === Главный контейнер ===
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # === Левая часть: форма добавления ===
        form_frame = ttk.LabelFrame(main_frame, text=" Новая заметка ", padding=10)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Заголовок
        ttk.Label(form_frame, text="Заголовок:").pack(anchor="w")
        self.title_entry = ttk.Entry(form_frame, width=35)
        self.title_entry.pack(fill=tk.X, pady=2)

        # Содержание
        ttk.Label(form_frame, text="Содержание:").pack(anchor="w")
        self.content_text = scrolledtext.ScrolledText(form_frame, width=35, height=10, wrap=tk.WORD)
        self.content_text.pack(fill=tk.X, pady=2)

        # Приоритет
        ttk.Label(form_frame, text="Приоритет:").pack(anchor="w")
        priority_frame = ttk.Frame(form_frame)
        priority_frame.pack(fill=tk.X, pady=2)
        self.priority_var = tk.StringVar(value="medium")
        for p in ["low", "medium", "high"]:
            ttk.Radiobutton(priority_frame, text=p.capitalize(), variable=self.priority_var, value=p).pack(side=tk.LEFT, expand=True)

        # Статус
        ttk.Label(form_frame, text="Статус:").pack(anchor="w")
        status_frame = ttk.Frame(form_frame)
        status_frame.pack(fill=tk.X, pady=2)
        self.status_var = tk.StringVar(value="active")
        for s in ["active", "done", "archived"]:
            ttk.Radiobutton(status_frame, text=s.capitalize(), variable=self.status_var, value=s).pack(side=tk.LEFT, expand=True)

        # Кнопка добавления
        ttk.Button(form_frame, text="Добавить заметку", command=self.add_note).pack(pady=12)

        # === Правая часть: список заметок ===
        list_frame = ttk.LabelFrame(main_frame, text=" Заметки ", padding=10)
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Поиск
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_notes())
        ttk.Button(search_frame, text="Очистить", command=self.clear_search).pack(side=tk.RIGHT)

        # Таблица
        columns = ("id", "title", "priority", "status", "date")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=100, anchor="w")
        self.tree.column("title", width=300)
        self.tree.column("id", width=50)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # События
        self.tree.bind("<Double-1>", self.show_details)
        self.tree.bind("<Delete>", self.delete_selected)

        # Кнопки
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", command=self.refresh_notes).pack(side=tk.LEFT)

    def add_note(self):
        """Добавляет новую заметку."""
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        if not title or not content:
            messagebox.showwarning("Ошибка", "Заполните заголовок и содержание!")
            return

        note = Note(
            title=title,
            content=content,
            priority=self.priority_var.get(),
            status=self.status_var.get()
        )
        if self.storage.save(note):
            messagebox.showinfo("Успех", f"Заметка добавлена (ID: {note.id})")
            self.clear_form()
            self.refresh_notes()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить заметку")

    def clear_form(self):
        """Очищает форму ввода."""
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)
        self.priority_var.set("medium")
        self.status_var.set("active")

    def refresh_notes(self):
        """Обновляет список заметок."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for note in self.storage.get_all():
            self.tree.insert("", tk.END, values=(
                note.id, note.title, note.priority, note.status, note.created_at[:10]
            ))

    def filter_notes(self):
        """Фильтрует заметки по поиску."""
        keyword = self.search_entry.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for note in self.storage.get_all():
            if keyword in note.title.lower() or keyword in note.content.lower():
                self.tree.insert("", tk.END, values=(
                    note.id, note.title, note.priority, note.status, note.created_at[:10]
                ))

    def clear_search(self):
        """Очищает поле поиска."""
        self.search_entry.delete(0, tk.END)
        self.refresh_notes()

    def show_details(self, event=None):
        """Открывает окно с деталями заметки."""
        selected = self.tree.selection()
        if not selected:
            return
        item = self.tree.item(selected[0])
        note_id = int(item["values"][0])
        note = next((n for n in self.storage.get_all() if n.id == note_id), None)
        if note:
            self.open_detail_window(note)

    def open_detail_window(self, note):
        """Окно просмотра заметки."""
        win = tk.Toplevel(self.root)
        win.title(f"Заметка #{note.id}: {note.title}")
        win.geometry("600x500")
        win.transient(self.root)
        win.grab_set()

        # Заголовок
        ttk.Label(win, text=note.title, font=("Segoe UI", 16, "bold")).pack(pady=10, anchor="w", padx=20)

        # Метаданные
        meta = f"Приоритет: {note.priority} | Статус: {note.status} | Создано: {note.created_at[:10]}"
        ttk.Label(win, text=meta, foreground="gray").pack(anchor="w", padx=20)

        # Содержание
        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Segoe UI", 11), padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        text.insert(tk.END, note.content)
        text.config(state=tk.DISABLED)

    def delete_selected(self, event=None):
        """Удаляет выбранную заметку."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Выберите", "Выберите заметку для удаления")
            return
        if messagebox.askyesno("Удалить", "Удалить выбранную заметку?"):
            note_id = int(self.tree.item(selected[0], "values")[0])
            if self.storage.delete(note_id):
                self.refresh_notes()
                messagebox.showinfo("Удалено", f"Заметка ID {note_id} удалена")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить")