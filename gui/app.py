import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from notebook import Storage, Note

BG_COLOR = "#FFF0F5"        # фон
PINK = "#FFC1CC"            # обычное состояние кнопки
DARK_PINK = "#FF69B4"       # нажатая / активная кнопка
WHITE = "#FFFFFF"
TEXT_COLOR = "#333333"

class NoteApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер заметок")
        self.root.geometry("950x650")
        self.root.minsize(850, 550)
        self.root.configure(bg=BG_COLOR)
        self.storage = Storage()

        self.priority_buttons = {}
        self.status_buttons = {}

        self.setup_styles()
        self.setup_ui()
        self.refresh_notes()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        style.configure('Pink.TButton',
                        background=PINK,
                        foreground=TEXT_COLOR,
                        font=('Segoe UI', 10, 'bold'),
                        padding=6)
        style.map('Pink.TButton',
                  background=[('active', DARK_PINK)],
                  foreground=[('active', 'white')])

        style.configure('Pink.TLabelframe',
                        background=BG_COLOR,
                        foreground=DARK_PINK,
                        font=('Segoe UI', 12, 'bold'))
        style.configure('Pink.TLabelframe.Label',
                        background=BG_COLOR,
                        foreground=DARK_PINK)

        style.configure('Treeview',
                        background=WHITE,
                        fieldbackground=WHITE,
                        font=('Segoe UI', 10),
                        rowheight=25)
        style.configure('Treeview.Heading',
                        background=PINK,
                        foreground=TEXT_COLOR,
                        font=('Segoe UI', 10, 'bold'))
        style.map('Treeview',
                  background=[('selected', DARK_PINK)])

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        form_frame = ttk.Labelframe(main_frame, text=" Новая заметка ", style='Pink.TLabelframe', padding=12)
        form_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))

        ttk.Label(form_frame, text="Заголовок:", background=BG_COLOR, font=('Segoe UI', 10)).pack(anchor="w", pady=(0, 3))
        self.title_entry = ttk.Entry(form_frame, width=38, font=('Segoe UI', 11))
        self.title_entry.pack(fill=tk.X, pady=2)

        ttk.Label(form_frame, text="Содержание:", background=BG_COLOR, font=('Segoe UI', 10)).pack(anchor="w", pady=(10, 3))
        self.content_text = scrolledtext.ScrolledText(form_frame, width=38, height=9, wrap=tk.WORD, font=('Segoe UI', 11))
        self.content_text.pack(fill=tk.X, pady=2)

        ttk.Label(form_frame, text="Приоритет:", background=BG_COLOR, font=('Segoe UI', 10)).pack(anchor="w", pady=(12, 3))
        priority_frame = ttk.Frame(form_frame)
        priority_frame.pack(fill=tk.X, pady=2)
        self.priority_var = tk.StringVar(value="medium")
        priorities = [("Низкий", "low"), ("Средний", "medium"), ("Высокий", "high")]
        for text, value in priorities:
            btn = tk.Button(priority_frame, text=text, bg=PINK, fg=TEXT_COLOR, font=('Segoe UI', 9, 'bold'),
                           relief='flat', command=lambda v=value: self.select_priority(v))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
            self.priority_buttons[value] = btn
        self.select_priority("medium")  # по умолчанию

        ttk.Label(form_frame, text="Статус:", background=BG_COLOR, font=('Segoe UI', 10)).pack(anchor="w", pady=(12, 3))
        status_frame = ttk.Frame(form_frame)
        status_frame.pack(fill=tk.X, pady=2)
        self.status_var = tk.StringVar(value="active")
        statuses = [("В работе", "active"), ("Готово", "done"), ("Архив", "archived")]
        for text, value in statuses:
            btn = tk.Button(status_frame, text=text, bg=PINK, fg=TEXT_COLOR, font=('Segoe UI', 9, 'bold'),
                           relief='flat', command=lambda v=value: self.select_status(v))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
            self.status_buttons[value] = btn
        self.select_status("active")  # по умолчанию

        add_btn = ttk.Button(form_frame, text="Добавить заметку", style='Pink.TButton', command=self.add_note)

        list_frame = ttk.Labelframe(main_frame, text=" Мои заметки ", style='Pink.TLabelframe', padding=12)
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 8))
        ttk.Label(search_frame, text="Поиск:", background=BG_COLOR, font=('Segoe UI', 10)).pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame, font=('Segoe UI', 11))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_notes())
        clear_btn = tk.Button(search_frame, text="Очистить", bg=DARK_PINK, fg="white", font=('Segoe UI', 9, 'bold'),
                             relief='flat', command=self.clear_search)
        clear_btn.pack(side=tk.RIGHT)

        columns = ("id", "title", "priority", "status", "date")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", style='Treeview')
        for col, text, width in [
            ("id", "ID", 50),
            ("title", "Заголовок", 320),
            ("priority", "Приоритет", 100),
            ("status", "Статус", 100),
            ("date", "Дата", 100)
        ]:
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor="w")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.tree.bind("<Double-1>", self.show_details)
        self.tree.bind("<Delete>", self.delete_selected)

        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(pady=8)
        ttk.Button(btn_frame, text="Удалить", style='Pink.TButton', command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Обновить", style='Pink.TButton', command=self.refresh_notes).pack(side=tk.LEFT)

    def select_priority(self, value):
        """Выделяет выбранную кнопку приоритета."""
        self.priority_var.set(value)
        for val, btn in self.priority_buttons.items():
            if val == value:
                btn.configure(bg=DARK_PINK, fg="white")
            else:
                btn.configure(bg=PINK, fg=TEXT_COLOR)

    def select_status(self, value):
        """Выделяет выбранную кнопку статуса."""
        self.status_var.set(value)
        for val, btn in self.status_buttons.items():
            if val == value:
                btn.configure(bg=DARK_PINK, fg="white")
            else:
                btn.configure(bg=PINK, fg=TEXT_COLOR)

    def add_note(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", tk.END).strip()
        if not title or not content:
            messagebox.showwarning("Ошибка", "Заполните заголовок и содержание!")
            return

        note = Note(title=title, content=content,
                    priority=self.priority_var.get(),
                    status=self.status_var.get())
        if self.storage.save(note):
            messagebox.showinfo("Готово!", f"Заметка добавлена (ID: {note.id})")
            self.clear_form()
            self.refresh_notes()
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить")

    def clear_form(self):
        self.title_entry.delete(0, tk.END)
        self.content_text.delete("1.0", tk.END)
        self.select_priority("medium")
        self.select_status("active")

    def refresh_notes(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for note in self.storage.get_all():
            priority_text = {"low": "Низкий", "medium": "Средний", "high": "Высокий"}[note.priority]
            status_text = {"active": "В работе", "done": "Готово", "archived": "Архив"}[note.status]
            self.tree.insert("", tk.END, values=(
                note.id, note.title, priority_text, status_text, note.created_at[:10]
            ))

    def filter_notes(self):
        keyword = self.search_entry.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for note in self.storage.get_all():
            if keyword in note.title.lower() or keyword in note.content.lower():
                priority_text = {"low": "Низкий", "medium": "Средний", "high": "Высокий"}[note.priority]
                status_text = {"active": "В работе", "done": "Готово", "archived": "Архив"}[note.status]
                self.tree.insert("", tk.END, values=(
                    note.id, note.title, priority_text, status_text, note.created_at[:10]
                ))

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.refresh_notes()

    def show_details(self, event=None):
        selected = self.tree.selection()
        if not selected: return
        item = self.tree.item(selected[0])
        note_id = int(item["values"][0])
        note = next((n for n in self.storage.get_all() if n.id == note_id), None)
        if note: self.open_detail_window(note)

    def open_detail_window(self, note):
        win = tk.Toplevel(self.root)
        win.title(f"Заметка #{note.id}")
        win.geometry("620x520")
        win.configure(bg=BG_COLOR)
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text=note.title, font=("Segoe UI", 16, "bold"), background=BG_COLOR, foreground=DARK_PINK).pack(pady=15, anchor="w", padx=20)
        meta = f"Приоритет: {note.priority.capitalize()} | Статус: {note.status.capitalize()} | {note.created_at[:10]}"
        ttk.Label(win, text=meta, background=BG_COLOR, foreground="gray", font=('Segoe UI', 10)).pack(anchor="w", padx=20)

        text = scrolledtext.ScrolledText(win, wrap=tk.WORD, font=("Segoe UI", 11), bg=WHITE, relief='flat', padx=10, pady=10)
        text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        text.insert(tk.END, note.content)
        text.config(state=tk.DISABLED)

    def delete_selected(self, event=None):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Выберите", "Выберите заметку для удаления")
            return
        if messagebox.askyesno("Удалить?", "Удалить выбранную заметку?"):
            note_id = int(self.tree.item(selected[0], "values")[0])
            if self.storage.delete(note_id):
                self.refresh_notes()
                messagebox.showinfo("Удалено", f"Заметка ID {note_id} удалена")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить")