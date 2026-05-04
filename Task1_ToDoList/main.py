import tkinter as tk
from tkinter import messagebox, font
import json
import os
from datetime import datetime

# Where tasks are saved
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "todos.json")

# Light colour palette
BG       = "#f5f5f5"
WHITE    = "#ffffff"
BORDER   = "#e0e0e0"
BLUE     = "#4a90d9"
GREEN    = "#4caf50"
RED      = "#e57373"
ORANGE   = "#ff9800"
DARK     = "#333333"
GREY     = "#757575"
LIGHT    = "#eeeeee"

PRIORITY_COLOR = {"High": RED, "Medium": ORANGE, "Low": GREEN}


def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


class TodoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("820x580")
        self.minsize(650, 450)
        self.configure(bg=BG)

        self.tasks = load_tasks()
        self.filter_mode = "All"

        self.normal_font  = font.Font(family="Segoe UI", size=10)
        self.bold_font    = font.Font(family="Segoe UI", size=10, weight="bold")
        self.small_font   = font.Font(family="Segoe UI", size=8)
        self.heading_font = font.Font(family="Segoe UI", size=16, weight="bold")

        self.build_ui()
        self.refresh()

    def build_ui(self):
        # ----- Header -----
        header = tk.Frame(self, bg=BLUE, pady=14)
        header.pack(fill="x")

        tk.Label(header, text="My To-Do List", bg=BLUE, fg=WHITE,
                 font=self.heading_font).pack(side="left", padx=20)

        self.stats_label = tk.Label(header, text="", bg=BLUE, fg=WHITE,
                                    font=self.small_font)
        self.stats_label.pack(side="right", padx=20)

        # ----- Toolbar -----
        toolbar = tk.Frame(self, bg=BG, pady=8)
        toolbar.pack(fill="x", padx=16)

        tk.Label(toolbar, text="Search:", bg=BG, fg=GREY,
                 font=self.normal_font).pack(side="left")

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        search_entry = tk.Entry(toolbar, textvariable=self.search_var,
                                font=self.normal_font, relief="solid", bd=1,
                                fg=DARK, bg=WHITE, width=22)
        search_entry.pack(side="left", padx=(4, 16), ipady=4)

        tk.Label(toolbar, text="Show:", bg=BG, fg=GREY,
                 font=self.normal_font).pack(side="left")

        for label in ("All", "Active", "Done"):
            tk.Button(toolbar, text=label, bg=WHITE, fg=DARK,
                      font=self.small_font, relief="solid", bd=1,
                      cursor="hand2", padx=8, pady=3,
                      command=lambda l=label: self.set_filter(l)
                      ).pack(side="left", padx=2)

        # ----- Main area -----
        main = tk.Frame(self, bg=BG)
        main.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        # Left: Add task form
        form_frame = tk.Frame(main, bg=WHITE, bd=1, relief="solid", padx=14, pady=14)
        form_frame.pack(side="left", fill="y", padx=(0, 12))

        tk.Label(form_frame, text="Add New Task", bg=WHITE, fg=BLUE,
                 font=self.bold_font).grid(row=0, column=0, columnspan=2,
                                           sticky="w", pady=(0, 10))

        self.title_var    = tk.StringVar()
        self.desc_var     = tk.StringVar()
        self.category_var = tk.StringVar()
        self.priority_var = tk.StringVar(value="Medium")

        fields = [
            ("Title *",      self.title_var),
            ("Description",  self.desc_var),
            ("Category",     self.category_var),
        ]

        for i, (lbl, var) in enumerate(fields):
            tk.Label(form_frame, text=lbl, bg=WHITE, fg=GREY,
                     font=self.small_font).grid(row=i*2+1, column=0,
                                                columnspan=2, sticky="w")
            tk.Entry(form_frame, textvariable=var, font=self.normal_font,
                     fg=DARK, bg=LIGHT, relief="flat",
                     width=22).grid(row=i*2+2, column=0, columnspan=2,
                                    sticky="ew", ipady=5, pady=(0, 6))

        tk.Label(form_frame, text="Priority", bg=WHITE, fg=GREY,
                 font=self.small_font).grid(row=7, column=0, columnspan=2, sticky="w")

        priority_frame = tk.Frame(form_frame, bg=WHITE)
        priority_frame.grid(row=8, column=0, columnspan=2, sticky="w", pady=(0, 12))
        for p in ("High", "Medium", "Low"):
            tk.Radiobutton(priority_frame, text=p, variable=self.priority_var,
                           value=p, bg=WHITE, fg=DARK,
                           font=self.small_font, activebackground=WHITE
                           ).pack(side="left")

        tk.Button(form_frame, text="Add Task", bg=BLUE, fg=WHITE,
                  font=self.bold_font, relief="flat", cursor="hand2",
                  padx=10, pady=7,
                  command=self.add_task).grid(row=9, column=0,
                                              columnspan=2, sticky="ew")

        tk.Button(form_frame, text="Clear Completed", bg=LIGHT, fg=GREY,
                  font=self.small_font, relief="flat", cursor="hand2",
                  padx=10, pady=5,
                  command=self.clear_done).grid(row=10, column=0,
                                                columnspan=2, sticky="ew",
                                                pady=(6, 0))

        # Right: Scrollable task list
        list_frame = tk.Frame(main, bg=BG)
        list_frame.pack(side="left", fill="both", expand=True)

        canvas = tk.Canvas(list_frame, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical",
                                 command=canvas.yview)
        self.task_container = tk.Frame(canvas, bg=BG)

        self.task_container.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        win_id = canvas.create_window((0, 0), window=self.task_container,
                                      anchor="nw")
        canvas.bind("<Configure>",
            lambda e: canvas.itemconfig(win_id, width=e.width))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.bind_all("<MouseWheel>",
            lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

    # ----- Logic -----

    def add_task(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Missing Title", "Please enter a task title.")
            return

        task = {
            "title":    title,
            "desc":     self.desc_var.get().strip(),
            "category": self.category_var.get().strip() or "General",
            "priority": self.priority_var.get(),
            "done":     False,
            "created":  datetime.now().strftime("%b %d, %Y"),
        }
        self.tasks.insert(0, task)
        save_tasks(self.tasks)

        self.title_var.set("")
        self.desc_var.set("")
        self.category_var.set("")
        self.priority_var.set("Medium")
        self.refresh()

    def toggle_done(self, index):
        self.tasks[index]["done"] = not self.tasks[index]["done"]
        save_tasks(self.tasks)
        self.refresh()

    def delete_task(self, index):
        if messagebox.askyesno("Delete", "Remove this task?"):
            del self.tasks[index]
            save_tasks(self.tasks)
            self.refresh()

    def clear_done(self):
        done_tasks = [t for t in self.tasks if t["done"]]
        if not done_tasks:
            messagebox.showinfo("Nothing to clear", "No completed tasks found.")
            return
        if messagebox.askyesno("Clear Completed", "Remove all completed tasks?"):
            self.tasks = [t for t in self.tasks if not t["done"]]
            save_tasks(self.tasks)
            self.refresh()

    def set_filter(self, mode):
        self.filter_mode = mode
        self.refresh()

    def refresh(self):
        # Clear existing cards
        for widget in self.task_container.winfo_children():
            widget.destroy()

        query = self.search_var.get().lower()
        visible = []

        for i, task in enumerate(self.tasks):
            if self.filter_mode == "Active" and task["done"]:
                continue
            if self.filter_mode == "Done" and not task["done"]:
                continue
            if query and query not in task["title"].lower() \
                     and query not in task.get("desc", "").lower():
                continue
            visible.append((i, task))

        if not visible:
            tk.Label(self.task_container, text="No tasks to show.",
                     bg=BG, fg=GREY, font=self.normal_font).pack(pady=40)
        else:
            for _, (real_i, task) in enumerate(visible):
                self.draw_task_card(real_i, task)

        done_count  = sum(1 for t in self.tasks if t["done"])
        total_count = len(self.tasks)
        self.stats_label.config(text=f"{done_count} / {total_count} completed")

    def draw_task_card(self, index, task):
        priority_color = PRIORITY_COLOR.get(task["priority"], ORANGE)
        is_done = task["done"]

        card = tk.Frame(self.task_container, bg=WHITE, bd=1,
                        relief="solid", pady=8, padx=10)
        card.pack(fill="x", pady=4, padx=2)

        # Priority dot
        dot = tk.Label(card, text="●", bg=WHITE,
                       fg=priority_color, font=self.bold_font)
        dot.pack(side="left", padx=(0, 8))

        # Task info
        info = tk.Frame(card, bg=WHITE)
        info.pack(side="left", fill="both", expand=True)

        title_style = {"font": self.bold_font, "bg": WHITE}
        if is_done:
            title_style["font"] = font.Font(family="Segoe UI", size=10,
                                            overstrike=True)
            title_style["fg"] = GREY
        else:
            title_style["fg"] = DARK

        tk.Label(info, text=task["title"],
                 **title_style, anchor="w").pack(fill="x")

        if task.get("desc"):
            tk.Label(info, text=task["desc"], bg=WHITE, fg=GREY,
                     font=self.small_font, anchor="w").pack(fill="x")

        meta_text = f"{task.get('category', 'General')}  |  {task['priority']} priority  |  {task.get('created', '')}"
        tk.Label(info, text=meta_text, bg=WHITE, fg=GREY,
                 font=self.small_font, anchor="w").pack(fill="x", pady=(2, 0))

        # Buttons
        btn_frame = tk.Frame(card, bg=WHITE)
        btn_frame.pack(side="right")

        done_label = "Undo" if is_done else "Done"
        tk.Button(btn_frame, text=done_label, bg=GREEN, fg=WHITE,
                  font=self.small_font, relief="flat", cursor="hand2",
                  padx=6, pady=3,
                  command=lambda i=index: self.toggle_done(i)
                  ).pack(side="left", padx=(0, 4))

        tk.Button(btn_frame, text="Delete", bg=RED, fg=WHITE,
                  font=self.small_font, relief="flat", cursor="hand2",
                  padx=6, pady=3,
                  command=lambda i=index: self.delete_task(i)
                  ).pack(side="left")


if __name__ == "__main__":
    app = TodoApp()
    app.mainloop()
