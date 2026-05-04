import tkinter as tk
from tkinter import font, messagebox
import random
import string
import pyperclip  # pip install pyperclip  (handles clipboard cross-platform)

# ── Palette (Dark, White, Yellow, Green) ───────────────────────────────────
BG       = "#161616"   # dark
PANEL    = "#222222"   # dark
DISPLAY  = "#101010"   # darker
ACCENT   = "#FACC15"   # yellow primary accent
GREEN    = "#22C55E"   # green
YELLOW   = "#EAB308"   # darker yellow for strength
RED_C    = "#EF4444"   # red
TEXT     = "#FFFFFF"   # white
TEXT_DIM = "#A3A3A3"
BTN_BG   = "#333333"
BTN_HOV  = "#444444"
BTN_GEN  = "#FACC15"   # yellow
BTN_GEN_H= "#EAB308"
BTN_CPY  = "#22C55E"   # green
BTN_CPY_H= "#16A34A"

# ── Strength bands ─────────────────────────────────────────────────────────
def password_strength(pw: str) -> tuple[str, str]:
    """Return (label, color) based on password composition."""
    score = 0
    score += min(len(pw) // 4, 4)                       # length  (max 4)
    score += 1 if any(c.isupper()   for c in pw) else 0
    score += 1 if any(c.islower()   for c in pw) else 0
    score += 1 if any(c.isdigit()   for c in pw) else 0
    score += 1 if any(c in string.punctuation for c in pw) else 0

    if score <= 3:   return "Weak",   RED_C
    if score <= 5:   return "Fair",   YELLOW
    if score <= 6:   return "Good",   ACCENT
    return            "Strong", GREEN


class PasswordGenerator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Generator")
        self.geometry("460x660")
        self.minsize(380, 540)
        self.resizable(True, True)
        self.configure(bg=BG)

        self._length     = tk.IntVar(value=16)
        self._use_upper  = tk.BooleanVar(value=True)
        self._use_lower  = tk.BooleanVar(value=True)
        self._use_digits = tk.BooleanVar(value=True)
        self._use_sym    = tk.BooleanVar(value=True)
        self._exclude    = tk.StringVar(value="")   # chars to exclude
        self._qty        = tk.IntVar(value=1)        # how many passwords

        self._setup_fonts()
        self._build_ui()

    # ── Fonts ─────────────────────────────────────────────────────────────
    def _setup_fonts(self):
        self.f_h1    = font.Font(family="Segoe UI", size=18, weight="bold")
        self.f_h2    = font.Font(family="Segoe UI", size=11, weight="bold")
        self.f_body  = font.Font(family="Segoe UI", size=10)
        self.f_pw    = font.Font(family="Consolas", size=13, weight="bold")
        self.f_small = font.Font(family="Segoe UI", size=9)

    # ── UI ───────────────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_header()
        self._build_controls()
        self._build_output()
        self._build_history()

    # Header ──────────────────────────────────────────────────────────────
    def _build_header(self):
        hdr = tk.Frame(self, bg=BTN_GEN, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🔐  Password Generator",
                 bg=BTN_GEN, fg=BG, font=self.f_h1).pack()
        tk.Label(hdr, text="Secure · Random · Customisable",
                 bg=BTN_GEN, fg=BG, font=self.f_small).pack(pady=(0, 4))

    # Controls ────────────────────────────────────────────────────────────
    def _build_controls(self):
        ctrl = tk.Frame(self, bg=PANEL, padx=24, pady=18)
        ctrl.pack(fill="x", padx=14, pady=(10, 6))

        # Length slider
        self._lbl_len = tk.Label(ctrl, text=f"Length: {self._length.get()}",
                                 bg=PANEL, fg=TEXT, font=self.f_h2, anchor="w")
        self._lbl_len.pack(fill="x")

        slider = tk.Scale(ctrl, from_=4, to=64, orient="horizontal",
                          variable=self._length, bg=PANEL, fg=ACCENT,
                          troughcolor=DISPLAY, highlightthickness=0,
                          activebackground=BTN_HOV, sliderrelief="flat",
                          command=self._on_slider)
        slider.pack(fill="x", pady=(2, 10))

        # Complexity checkboxes
        tk.Label(ctrl, text="Include:", bg=PANEL, fg=TEXT_DIM,
                 font=self.f_body, anchor="w").pack(fill="x")

        box_frame = tk.Frame(ctrl, bg=PANEL)
        box_frame.pack(fill="x", pady=(4, 8))

        options = [
            ("A–Z  Uppercase",  self._use_upper),
            ("a–z  Lowercase",  self._use_lower),
            ("0–9  Digits",     self._use_digits),
            ("!@#  Symbols",    self._use_sym),
        ]
        for i, (lbl, var) in enumerate(options):
            cb = tk.Checkbutton(box_frame, text=lbl, variable=var,
                                bg=PANEL, fg=TEXT, selectcolor=DISPLAY,
                                activebackground=PANEL, activeforeground=ACCENT,
                                font=self.f_body, anchor="w", cursor="hand2")
            cb.grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 16), pady=2)

        # Exclude characters
        ex_frame = tk.Frame(ctrl, bg=PANEL)
        ex_frame.pack(fill="x", pady=(4, 8))
        tk.Label(ex_frame, text="Exclude chars:", bg=PANEL, fg=TEXT_DIM,
                 font=self.f_body).pack(side="left")
        tk.Entry(ex_frame, textvariable=self._exclude, width=14,
                 bg=DISPLAY, fg=TEXT, insertbackground=ACCENT,
                 relief="flat", font=self.f_body).pack(side="left", padx=(8, 0), ipady=4)

        # Quantity
        qty_frame = tk.Frame(ctrl, bg=PANEL)
        qty_frame.pack(fill="x", pady=(0, 4))
        tk.Label(qty_frame, text="How many:", bg=PANEL, fg=TEXT_DIM,
                 font=self.f_body).pack(side="left")
        for n in (1, 3, 5, 10):
            rb = tk.Radiobutton(qty_frame, text=str(n), variable=self._qty,
                                value=n, bg=PANEL, fg=TEXT, selectcolor=DISPLAY,
                                activebackground=PANEL, activeforeground=ACCENT,
                                font=self.f_body, cursor="hand2")
            rb.pack(side="left", padx=6)

        # Generate button
        gen_btn = tk.Label(ctrl, text="⚡  Generate Password",
                           bg=BTN_GEN, fg=BG, font=self.f_h2,
                           relief="flat", cursor="hand2", pady=10)
        gen_btn.pack(fill="x", pady=(10, 0))
        gen_btn.bind("<Enter>",    lambda e: gen_btn.configure(bg=BTN_GEN_H))
        gen_btn.bind("<Leave>",    lambda e: gen_btn.configure(bg=BTN_GEN))
        gen_btn.bind("<Button-1>", lambda e: self._generate())

        self.bind("<Return>", lambda e: self._generate())   # Enter key

    # Output ──────────────────────────────────────────────────────────────
    def _build_output(self):
        out = tk.Frame(self, bg=DISPLAY, padx=18, pady=16)
        out.pack(fill="x", padx=14, pady=(0, 6))
        # Keep wraplength in sync with window width
        self.bind("<Configure>", self._on_resize)

        # Password display
        self.pw_var = tk.StringVar(value="Click Generate ⚡")
        self._pw_label = tk.Label(out, textvariable=self.pw_var, bg=DISPLAY,
                                  fg=TEXT_DIM, font=self.f_pw,
                                  wraplength=400, justify="center")
        self._pw_label.pack(fill="x", pady=(0, 4))

        # Strength meter
        meter_row = tk.Frame(out, bg=DISPLAY)
        meter_row.pack(fill="x", pady=(8, 4))

        tk.Label(meter_row, text="Strength:", bg=DISPLAY, fg=TEXT_DIM,
                 font=self.f_small).pack(side="left")
        self._str_label = tk.Label(meter_row, text="—", bg=DISPLAY,
                                   fg=TEXT_DIM, font=self.f_small,
                                   width=8, anchor="w")
        self._str_label.pack(side="left", padx=(6, 12))

        self._meter_canvas = tk.Canvas(meter_row, height=10, width=160,
                                       bg=PANEL, highlightthickness=0)
        self._meter_canvas.pack(side="left")

        # Copy button
        copy_btn = tk.Label(out, text="📋  Copy to Clipboard",
                            bg=BTN_CPY, fg=BG, font=self.f_body,
                            relief="flat", cursor="hand2", pady=6)
        copy_btn.pack(fill="x", pady=(8, 0))
        copy_btn.bind("<Enter>",    lambda e: copy_btn.configure(bg=BTN_CPY_H))
        copy_btn.bind("<Leave>",    lambda e: copy_btn.configure(bg=BTN_CPY))
        copy_btn.bind("<Button-1>", lambda e: self._copy())

        self.bind("<Control-c>", lambda e: self._copy())   # Ctrl+C shortcut

    # History ─────────────────────────────────────────────────────────────
    def _build_history(self):
        hist = tk.Frame(self, bg=PANEL)
        hist.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        hdr_row = tk.Frame(hist, bg=PANEL)
        hdr_row.pack(fill="x", padx=10, pady=(6, 0))
        tk.Label(hdr_row, text="📜 History", bg=PANEL, fg=TEXT_DIM,
                 font=self.f_small).pack(side="left")
        clr = tk.Label(hdr_row, text="Clear", bg=PANEL, fg=RED_C,
                       font=self.f_small, cursor="hand2")
        clr.pack(side="right")
        clr.bind("<Button-1>", self._clear_history)

        self.hist_box = tk.Text(hist, bg=PANEL, fg=TEXT_DIM,
                                font=font.Font(family="Consolas", size=9),
                                height=5, relief="flat", state="disabled",
                                wrap="word", cursor="arrow",
                                selectbackground=BTN_BG)
        # Add a scrollbar
        scrollbar = tk.Scrollbar(hist, command=self.hist_box.yview, troughcolor=PANEL, bg=PANEL)
        self.hist_box.configure(yscrollcommand=scrollbar.set)
        
        # Pack them
        scrollbar.pack(side="right", fill="y", pady=(4, 8))
        self.hist_box.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=(4, 8))

    # ── Actions ──────────────────────────────────────────────────────────
    def _on_resize(self, event):
        """Keep password label wraplength in sync with window width."""
        if event.widget is self:
            new_wrap = max(200, event.width - 80)
            self._pw_label.configure(wraplength=new_wrap)

    def _on_slider(self, val):
        self._lbl_len.configure(text=f"Length: {val}")

    def _generate(self):
        pool = ""
        if self._use_upper.get():  pool += string.ascii_uppercase
        if self._use_lower.get():  pool += string.ascii_lowercase
        if self._use_digits.get(): pool += string.digits
        if self._use_sym.get():    pool += string.punctuation

        excluded = self._exclude.get()
        pool = "".join(c for c in pool if c not in excluded)

        if not pool:
            messagebox.showwarning("No Characters",
                "Please select at least one character type.")
            return

        length = self._length.get()
        passwords = []
        for _ in range(self._qty.get()):
            pw = "".join(random.SystemRandom().choices(pool, k=length))
            passwords.append(pw)

        display = "\n".join(passwords) if len(passwords) == 1 else "\n".join(passwords)
        self.pw_var.set(display)
        self._pw_label.configure(fg=TEXT)

        # Strength for the first password
        label, color = password_strength(passwords[0])
        self._str_label.configure(text=label, fg=color)
        self._draw_meter(label, color)

        # Add to history
        self._push_history(passwords)

        # Stash latest batch for copy
        self._last_passwords = passwords

    def _draw_meter(self, label: str, color: str):
        self._meter_canvas.delete("all")
        w = 160
        segments = {"Weak": 1, "Fair": 2, "Good": 3, "Strong": 4}
        filled = segments.get(label, 0)
        seg_w = w // 4 - 3
        for i in range(4):
            x0 = i * (seg_w + 4)
            x1 = x0 + seg_w
            fill = color if i < filled else PANEL
            self._meter_canvas.create_rectangle(x0, 0, x1, 10,
                                                fill=fill, outline="")

    def _copy(self):
        passwords = getattr(self, "_last_passwords", None)
        if not passwords:
            return
        text = "\n".join(passwords)
        try:
            pyperclip.copy(text)
        except Exception:
            self.clipboard_clear()
            self.clipboard_append(text)
        # Flash feedback
        self.pw_var.set("✅ Copied!")
        self._pw_label.configure(fg=GREEN)
        self.after(1200, lambda: self.pw_var.set("\n".join(passwords)))
        self.after(1200, lambda: self._pw_label.configure(fg=TEXT))

    def _push_history(self, passwords: list[str]):
        self.hist_box.configure(state="normal")
        for pw in passwords:
            lbl, _ = password_strength(pw)
            self.hist_box.insert("end", f"[{lbl:6}] {pw}\n")
        self.hist_box.see("end")
        self.hist_box.configure(state="disabled")

    def _clear_history(self, _event=None):
        self.hist_box.configure(state="normal")
        self.hist_box.delete("1.0", "end")
        self.hist_box.configure(state="disabled")


if __name__ == "__main__":
    app = PasswordGenerator()
    app.mainloop()
