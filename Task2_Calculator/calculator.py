import tkinter as tk
from tkinter import font
import math

# ── Palette ────────────────────────────────────────────────────────────────
BG        = "#0f0f1a"   # deep navy background
PANEL     = "#1a1a2e"   # card / panel
DISPLAY   = "#12122b"   # display area
BTN_NUM   = "#1e1e3a"   # number button
BTN_OP    = "#2d2b55"   # operator button
BTN_EQ    = "#7c5cbf"   # equals button  (purple accent)
BTN_SPEC  = "#1a2a3a"   # special (C, ±, %)
HOVER_NUM = "#2e2e52"
HOVER_OP  = "#3d3b70"
HOVER_EQ  = "#9b74d4"
HOVER_SP  = "#243545"
TEXT      = "#e8e8ff"   # main text
TEXT_DIM  = "#8888bb"   # secondary text
ACCENT    = "#a78bfa"   # purple accent
GREEN     = "#34d399"   # positive result
RED_ERR   = "#f87171"   # error

# ── Button layout  [label, col, row, colspan, kind] ────────────────────────
# kind: num | op | eq | spec
BUTTONS = [
    # Row 0
    ("C",   0, 0, 1, "spec"), ("±",  1, 0, 1, "spec"),
    ("%",   2, 0, 1, "spec"), ("÷",  3, 0, 1, "op"),
    # Row 1
    ("7",   0, 1, 1, "num"),  ("8",  1, 1, 1, "num"),
    ("9",   2, 1, 1, "num"),  ("×",  3, 1, 1, "op"),
    # Row 2
    ("4",   0, 2, 1, "num"),  ("5",  1, 2, 1, "num"),
    ("6",   2, 2, 1, "num"),  ("-",  3, 2, 1, "op"),
    # Row 3
    ("1",   0, 3, 1, "num"),  ("2",  1, 3, 1, "num"),
    ("3",   2, 3, 1, "num"),  ("+",  3, 3, 1, "op"),
    # Row 4
    ("0",   0, 4, 2, "num"),  (".",  2, 4, 1, "num"),
    ("=",   3, 4, 1, "eq"),
]

KIND_COLORS = {
    "num":  (BTN_NUM,  HOVER_NUM, TEXT),
    "op":   (BTN_OP,   HOVER_OP,  ACCENT),
    "eq":   (BTN_EQ,   HOVER_EQ,  TEXT),
    "spec": (BTN_SPEC, HOVER_SP,  TEXT_DIM),
}

KEYS_MAP = {
    "0":"0","1":"1","2":"2","3":"3","4":"4",
    "5":"5","6":"6","7":"7","8":"8","9":"9",
    ".":".", "+":"+", "-":"-", "*":"×", "/":"÷",
    "Return":"=", "KP_Enter":"=",
    "percent":"%", "BackSpace":"⌫",
    "Escape":"C", "equal":"=",
}


class Calculator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculator")
        self.geometry("360x600")
        self.resizable(False, False)
        self.configure(bg=BG)

        self._expression = ""  # running expression string
        self._just_computed = False

        self._setup_fonts()
        self._build_ui()
        self._bind_keys()

    # ── Fonts ──────────────────────────────────────────────────────────────
    def _setup_fonts(self):
        self.f_expr   = font.Font(family="Segoe UI",   size=12)
        self.f_disp   = font.Font(family="Segoe UI",   size=28, weight="bold")
        self.f_btn    = font.Font(family="Segoe UI",   size=15, weight="bold")
        self.f_small  = font.Font(family="Segoe UI",   size=9)
        self.f_hist   = font.Font(family="Consolas",   size=9)

    # ── UI ──────────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_display()
        self._build_history()
        self._build_keyboard_hint()
        self._build_keypad()

    def _build_display(self):
        disp = tk.Frame(self, bg=DISPLAY, pady=10)
        disp.pack(fill="x", padx=12, pady=(14, 0))

        # Expression (top — smaller, dimmed)
        self.expr_var = tk.StringVar(value="")
        tk.Label(disp, textvariable=self.expr_var, bg=DISPLAY, fg=TEXT_DIM,
                 font=self.f_expr, anchor="e", width=26
                 ).pack(fill="x", padx=14)

        # Main number display
        self.disp_var = tk.StringVar(value="0")
        tk.Label(disp, textvariable=self.disp_var, bg=DISPLAY, fg=TEXT,
                 font=self.f_disp, anchor="e", width=13
                 ).pack(fill="x", padx=14, pady=(4, 10))

    def _build_history(self):
        hist_frame = tk.Frame(self, bg=PANEL)
        hist_frame.pack(fill="x", padx=12, pady=(6, 0))
        tk.Label(hist_frame, text="History", bg=PANEL, fg=TEXT_DIM,
                 font=self.f_small, anchor="w").pack(fill="x", padx=10, pady=(4, 0))
        self.history_box = tk.Text(hist_frame, bg=PANEL, fg=TEXT_DIM,
                                   font=self.f_hist, height=3,
                                   relief="flat", state="disabled",
                                   wrap="word", cursor="arrow",
                                   selectbackground=BTN_OP)
        self.history_box.pack(fill="x", padx=10, pady=(2, 6))

    def _build_keyboard_hint(self):
        hint = tk.Frame(self, bg=BG)
        hint.pack(fill="x", padx=12, pady=(4, 0))
        tk.Label(hint, text="⌨  Keyboard & mouse supported",
                 bg=BG, fg=TEXT_DIM, font=self.f_small, anchor="w"
                 ).pack(side="left")

    def _build_keypad(self):
        pad = tk.Frame(self, bg=BG)
        pad.pack(fill="both", expand=True, padx=12, pady=10)

        for label, col, row, cspan, kind in BUTTONS:
            bg, hbg, fg = KIND_COLORS[kind]
            self._make_button(pad, label, col, row, cspan, bg, hbg, fg)

        for c in range(4):
            pad.columnconfigure(c, weight=1, minsize=78)
        for r in range(5):
            pad.rowconfigure(r, weight=1, minsize=62)

    def _make_button(self, parent, label, col, row, cspan, bg, hbg, fg):
        btn = tk.Label(parent, text=label, bg=bg, fg=fg,
                       font=self.f_btn, relief="flat", cursor="hand2",
                       activebackground=hbg, activeforeground=fg)
        btn.grid(row=row, column=col, columnspan=cspan,
                 padx=4, pady=4, sticky="nsew")

        # Hover animation
        btn.bind("<Enter>",  lambda e, b=btn, c=hbg: b.configure(bg=c))
        btn.bind("<Leave>",  lambda e, b=btn, c=bg:  b.configure(bg=c))
        btn.bind("<Button-1>", lambda e, b=btn, c=hbg: self._on_press(b, label, c))
        btn.bind("<ButtonRelease-1>", lambda e, b=btn, c=hbg: b.configure(bg=c))

    # ── Button press ────────────────────────────────────────────────────────
    def _on_press(self, btn, label, hbg):
        btn.configure(bg=hbg)
        self._handle(label)

    def _handle(self, label):
        cur = self.disp_var.get()

        if label == "C":
            self._expression = ""
            self.disp_var.set("0")
            self.expr_var.set("")
            self._just_computed = False

        elif label == "⌫":
            if self._just_computed:
                self._expression = ""
                self.disp_var.set("0")
                self._just_computed = False
            else:
                new = cur[:-1] if len(cur) > 1 else "0"
                self.disp_var.set(new)

        elif label == "±":
            try:
                val = float(cur)
                toggled = -val
                self.disp_var.set(self._fmt(toggled))
            except ValueError:
                pass

        elif label == "%":
            try:
                val = float(cur) / 100
                self.disp_var.set(self._fmt(val))
                self._add_history(f"{cur}%  =  {self._fmt(val)}")
            except ValueError:
                pass

        elif label in ("+", "-", "×", "÷"):
            if self._just_computed:
                self._expression = cur + " " + label
                self._just_computed = False
            else:
                self._expression = (self._expression or cur) + " " + label
            self.expr_var.set(self._expression)
            self.disp_var.set("0")

        elif label == "=":
            expr_str = (self._expression + " " + cur).strip()
            result, error = self._evaluate(expr_str)
            if error:
                self.disp_var.set(error)
                self.disp_var._label_fg = RED_ERR  # visual cue (patched below)
                self._update_display_color(RED_ERR)
            else:
                self._add_history(f"{expr_str}  =  {self._fmt(result)}")
                self.disp_var.set(self._fmt(result))
                self._update_display_color(GREEN)
                self.after(300, lambda: self._update_display_color(TEXT))
            self.expr_var.set(expr_str + "  =")
            self._expression = ""
            self._just_computed = True

        else:
            # Digit or decimal
            if self._just_computed:
                self.disp_var.set(label)
                self._expression = ""
                self._just_computed = False
            elif cur == "0" and label != ".":
                self.disp_var.set(label)
            else:
                if label == "." and "." in cur:
                    return
                self.disp_var.set(cur + label)

    def _update_display_color(self, color):
        # Walk widgets to find display label
        self._disp_color = color
        for w in self.winfo_children():
            for w2 in w.winfo_children():
                if isinstance(w2, tk.Label):
                    try:
                        if w2.cget("textvariable") == str(self.disp_var):
                            w2.configure(fg=color)
                    except Exception:
                        pass

    def _update_display_color(self, color):
        try:
            self._main_disp_label.configure(fg=color)
        except AttributeError:
            pass

    def _build_display(self):
        disp = tk.Frame(self, bg=DISPLAY, pady=10)
        disp.pack(fill="x", padx=12, pady=(14, 0))

        self.expr_var = tk.StringVar(value="")
        tk.Label(disp, textvariable=self.expr_var, bg=DISPLAY, fg=TEXT_DIM,
                 font=self.f_expr, anchor="e").pack(fill="x", padx=14)

        self.disp_var = tk.StringVar(value="0")
        self._main_disp_label = tk.Label(disp, textvariable=self.disp_var,
                                         bg=DISPLAY, fg=TEXT,
                                         font=self.f_disp, anchor="e")
        self._main_disp_label.pack(fill="x", padx=14, pady=(4, 10))

    # ── Evaluate ────────────────────────────────────────────────────────────
    def _evaluate(self, expr: str):
        """Safely evaluate an expression like '7 × 3 + 2'."""
        try:
            safe = (expr
                    .replace("×", "*")
                    .replace("÷", "/")
                    .replace(",", ""))
            result = eval(safe, {"__builtins__": {}}, {})  # noqa: S307
            return result, None
        except ZeroDivisionError:
            return None, "÷ 0  Error"
        except Exception:
            return None, "Syntax Error"

    # ── History ─────────────────────────────────────────────────────────────
    def _add_history(self, text):
        self.history_box.configure(state="normal")
        self.history_box.insert("end", text + "\n")
        self.history_box.see("end")
        self.history_box.configure(state="disabled")

    # ── Format ──────────────────────────────────────────────────────────────
    @staticmethod
    def _fmt(val):
        if isinstance(val, float) and val.is_integer():
            return str(int(val))
        if isinstance(val, float):
            return f"{val:.8g}"
        return str(val)

    # ── Keyboard bindings ───────────────────────────────────────────────────
    def _bind_keys(self):
        self.bind("<Key>", self._on_key)

    def _on_key(self, event):
        sym = event.keysym
        char = event.char
        # Prefer keysym map first
        mapped = KEYS_MAP.get(sym) or KEYS_MAP.get(char)
        if mapped:
            self._handle(mapped)
        elif char and char in "0123456789.":
            self._handle(char)


if __name__ == "__main__":
    app = Calculator()
    app.mainloop()
