import tkinter as tk
from tkinter import font
import random

# ── Palette (Dark, White, Yellow, Green) ───────────────────────────────────
BG       = "#161616"
PANEL    = "#222222"
DISPLAY  = "#101010"
ACCENT   = "#FACC15"   # yellow
GREEN    = "#22C55E"   # green (win)
RED_C    = "#EF4444"   # red (lose)
TEXT     = "#FFFFFF"
TEXT_DIM = "#A3A3A3"
BTN_BG   = "#333333"
BTN_HOV  = "#444444"

CHOICES = ["Rock", "Paper", "Scissors"]
EMOJIS = {"Rock": "✊", "Paper": "✋", "Scissors": "✌️"}

class RockPaperScissors(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Rock Paper Scissors")
        self.geometry("480x620")
        self.minsize(400, 560)
        self.configure(bg=BG)

        self.user_score = 0
        self.comp_score = 0

        self._setup_fonts()
        self._build_ui()

    def _setup_fonts(self):
        self.f_h1   = font.Font(family="Segoe UI", size=20, weight="bold")
        self.f_h2   = font.Font(family="Segoe UI", size=14, weight="bold")
        self.f_body = font.Font(family="Segoe UI", size=11)
        self.f_big  = font.Font(family="Segoe UI", size=36)
        self.f_res  = font.Font(family="Segoe UI", size=16, weight="bold")
        self.f_btn  = font.Font(family="Segoe UI", size=14, weight="bold")

    def _build_ui(self):
        # 1. Header
        hdr = tk.Frame(self, bg=ACCENT, pady=12)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Rock Paper Scissors", bg=ACCENT, fg=BG, font=self.f_h1).pack()
        tk.Label(hdr, text="First to 5 or play endlessly!", bg=ACCENT, fg=BG, font=self.f_body).pack()

        # 2. Scoreboard
        score_fr = tk.Frame(self, bg=PANEL, padx=20, pady=16)
        score_fr.pack(fill="x", padx=16, pady=16)
        
        score_grid = tk.Frame(score_fr, bg=PANEL)
        score_grid.pack(expand=True)
        score_grid.columnconfigure(0, minsize=100)
        score_grid.columnconfigure(1, minsize=40)
        score_grid.columnconfigure(2, minsize=100)

        # User Score
        tk.Label(score_grid, text="You", bg=PANEL, fg=TEXT_DIM, font=self.f_h2).grid(row=0, column=0)
        self.lbl_score_usr = tk.Label(score_grid, text="0", bg=PANEL, fg=TEXT, font=self.f_big)
        self.lbl_score_usr.grid(row=1, column=0)
        
        # Divider
        tk.Label(score_grid, text="-", bg=PANEL, fg=TEXT_DIM, font=self.f_big).grid(row=1, column=1)

        # Comp Score
        tk.Label(score_grid, text="Computer", bg=PANEL, fg=TEXT_DIM, font=self.f_h2).grid(row=0, column=2)
        self.lbl_score_comp = tk.Label(score_grid, text="0", bg=PANEL, fg=TEXT, font=self.f_big)
        self.lbl_score_comp.grid(row=1, column=2)

        # 3. Arena (Displays choice & result)
        self.arena = tk.Frame(self, bg=DISPLAY, pady=20)
        self.arena.pack(fill="both", expand=True, padx=16)
        
        # Result Text
        self.lbl_result = tk.Label(self.arena, text="Make your move!", bg=DISPLAY, fg=ACCENT, font=self.f_res)
        self.lbl_result.pack(pady=(0, 16))

        # Choices display
        choice_fr = tk.Frame(self.arena, bg=DISPLAY)
        choice_fr.pack(expand=True)
        
        self.lbl_choice_usr = tk.Label(choice_fr, text="❔", bg=DISPLAY, fg=TEXT, font=font.Font(size=48))
        self.lbl_choice_usr.grid(row=0, column=0, padx=20)

        tk.Label(choice_fr, text="VS", bg=DISPLAY, fg=TEXT_DIM, font=self.f_h2).grid(row=0, column=1, padx=10)

        self.lbl_choice_comp = tk.Label(choice_fr, text="💻", bg=DISPLAY, fg=TEXT, font=font.Font(size=48))
        self.lbl_choice_comp.grid(row=0, column=2, padx=20)
        
        self.lbl_desc_usr = tk.Label(choice_fr, text="", bg=DISPLAY, fg=TEXT_DIM, font=self.f_body)
        self.lbl_desc_usr.grid(row=1, column=0)
        self.lbl_desc_comp = tk.Label(choice_fr, text="", bg=DISPLAY, fg=TEXT_DIM, font=self.f_body)
        self.lbl_desc_comp.grid(row=1, column=2)

        # 4. Controls (Buttons)
        ctrls = tk.Frame(self, bg=BG)
        ctrls.pack(fill="x", side="bottom", pady=20, padx=12)
        
        btn_fr = tk.Frame(ctrls, bg=BG)
        btn_fr.pack(expand=True)

        for c in CHOICES:
            lbl = f"{EMOJIS[c]} {c}"
            btn = tk.Label(btn_fr, text=lbl, bg=BTN_BG, fg=TEXT, font=self.f_btn, 
                           pady=12, padx=16, cursor="hand2", width=8)
            btn.pack(side="left", padx=6)
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=BTN_HOV))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=BTN_BG))
            btn.bind("<Button-1>", lambda e, choice=c: self.play_round(choice))

        # Reset Game Link
        reset_lbl = tk.Label(ctrls, text="↻ Reset Scores", bg=BG, fg=TEXT_DIM, font=self.f_body, cursor="hand2")
        reset_lbl.pack(pady=(16, 0))
        reset_lbl.bind("<Enter>", lambda e: reset_lbl.configure(fg=TEXT))
        reset_lbl.bind("<Leave>", lambda e: reset_lbl.configure(fg=TEXT_DIM))
        reset_lbl.bind("<Button-1>", lambda e: self.reset_game())

    def play_round(self, user_choice):
        comp_choice = random.choice(CHOICES)
        
        # Determine winner
        if user_choice == comp_choice:
            status = "tie"
        elif (user_choice == "Rock" and comp_choice == "Scissors") or \
             (user_choice == "Paper" and comp_choice == "Rock") or \
             (user_choice == "Scissors" and comp_choice == "Paper"):
             status = "win"
        else:
             status = "lose"
        
        self.update_ui(user_choice, comp_choice, status)

    def update_ui(self, user, comp, status):
        # Update Choices
        self.lbl_choice_usr.config(text=EMOJIS[user])
        self.lbl_choice_comp.config(text=EMOJIS[comp])
        self.lbl_desc_usr.config(text=user)
        self.lbl_desc_comp.config(text=comp)

        # Update Result & Score
        if status == "win":
            self.user_score += 1
            self.lbl_score_usr.config(text=str(self.user_score))
            self.lbl_result.config(text="🎉 You Win!", fg=GREEN)
            self.arena.config(highlightbackground=GREEN, highlightthickness=2)
        elif status == "lose":
            self.comp_score += 1
            self.lbl_score_comp.config(text=str(self.comp_score))
            self.lbl_result.config(text="💻 Computer Wins!", fg=RED_C)
            self.arena.config(highlightbackground=RED_C, highlightthickness=2)
        else:
            self.lbl_result.config(text="🤝 It's a Tie!", fg=ACCENT)
            self.arena.config(highlightbackground=TEXT_DIM, highlightthickness=2)

    def reset_game(self):
        self.user_score = 0
        self.comp_score = 0
        self.lbl_score_usr.config(text="0")
        self.lbl_score_comp.config(text="0")
        self.lbl_choice_usr.config(text="❔")
        self.lbl_choice_comp.config(text="💻")
        self.lbl_desc_usr.config(text="")
        self.lbl_desc_comp.config(text="")
        self.lbl_result.config(text="Make your move!", fg=ACCENT)
        self.arena.config(highlightthickness=0)

if __name__ == "__main__":
    app = RockPaperScissors()
    app.mainloop()
