import tkinter as tk
from tkinter import font, messagebox
import json
import os
import uuid

# ── Palette (Dark, White, Yellow, Green) ───────────────────────────────────
BG       = "#161616"
PANEL    = "#222222"
DISPLAY  = "#101010"
ACCENT   = "#FACC15"   # yellow
GREEN    = "#22C55E"   # green
RED_C    = "#EF4444"   # red
TEXT     = "#FFFFFF"
TEXT_DIM = "#A3A3A3"
BTN_BG   = "#333333"
BTN_HOV  = "#444444"

DATA_FILE = "contacts.json"

class ContactBook(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Contact Book")
        self.geometry("720x540")
        self.minsize(640, 480)
        self.configure(bg=BG)

        self.contacts = self.load_data()
        self.current_selected_id = None

        self._setup_fonts()
        self._build_ui()
        self.refresh_list()

    def _setup_fonts(self):
        self.f_h1   = font.Font(family="Segoe UI", size=16, weight="bold")
        self.f_h2   = font.Font(family="Segoe UI", size=12, weight="bold")
        self.f_body = font.Font(family="Segoe UI", size=10)
        self.f_btn  = font.Font(family="Segoe UI", size=10, weight="bold")

    def _build_ui(self):
        # Master Layout: Left (List + Search) | Right (Form)
        self.left_panel = tk.Frame(self, bg=PANEL, width=280)
        self.left_panel.pack(side="left", fill="y", padx=(10, 5), pady=10)
        self.left_panel.pack_propagate(False)

        self.right_panel = tk.Frame(self, bg=DISPLAY)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        self._build_left_panel()
        self._build_right_panel()

    def _build_left_panel(self):
        hdr = tk.Frame(self.left_panel, bg=ACCENT, pady=8)
        hdr.pack(fill="x")
        tk.Label(hdr, text="Contacts", bg=ACCENT, fg=BG, font=self.f_h1).pack()

        # Search Bar
        search_fr = tk.Frame(self.left_panel, bg=PANEL, pady=10, padx=10)
        search_fr.pack(fill="x")
        tk.Label(search_fr, text="Search:", bg=PANEL, fg=TEXT_DIM, font=self.f_body).pack(side="left", padx=(0, 4))
        
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *args: self.refresh_list())
        
        search_entry = tk.Entry(search_fr, textvariable=self.search_var, bg=DISPLAY, fg=TEXT, 
                                insertbackground=ACCENT, relief="flat", font=self.f_body)
        search_entry.pack(fill="x", expand=True, ipady=4)

        # Listbox Wrapper
        list_fr = tk.Frame(self.left_panel, bg=DISPLAY)
        list_fr.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Scrollbar
        scroll = tk.Scrollbar(list_fr, bg=DISPLAY, troughcolor=PANEL)
        scroll.pack(side="right", fill="y")

        # Listbox
        self.listbox = tk.Listbox(list_fr, bg=DISPLAY, fg=TEXT, font=self.f_body, 
                                  selectbackground=ACCENT, selectforeground=BG,
                                  relief="flat", highlightthickness=0, yscrollcommand=scroll.set)
        self.listbox.pack(side="left", fill="both", expand=True)
        scroll.config(command=self.listbox.yview)

        self.listbox.bind("<<ListboxSelect>>", self.on_select)

    def _build_right_panel(self):
        # Header
        self.lbl_form_title = tk.Label(self.right_panel, text="New Contact", bg=DISPLAY, fg=ACCENT, font=self.f_h1, anchor="w")
        self.lbl_form_title.pack(fill="x", padx=20, pady=(20, 10))

        form_fr = tk.Frame(self.right_panel, bg=DISPLAY)
        form_fr.pack(fill="both", expand=True, padx=20)

        # Fields
        self.vars = {
            "name": tk.StringVar(),
            "phone": tk.StringVar(),
            "email": tk.StringVar(),
            "address": tk.StringVar()
        }

        labels = ["Name *", "Phone *", "Email", "Address"]
        keys = ["name", "phone", "email", "address"]

        for i, (lbl, key) in enumerate(zip(labels, keys)):
            tk.Label(form_fr, text=lbl, bg=DISPLAY, fg=TEXT_DIM, font=self.f_body, anchor="w").grid(row=i*2, column=0, sticky="w", pady=(10, 2))
            entry = tk.Entry(form_fr, textvariable=self.vars[key], bg=PANEL, fg=TEXT, insertbackground=ACCENT, relief="flat", font=self.f_h2)
            entry.grid(row=i*2 + 1, column=0, sticky="we", ipady=6)
        
        form_fr.columnconfigure(0, weight=1)

        # Buttons
        btn_fr = tk.Frame(self.right_panel, bg=DISPLAY)
        btn_fr.pack(fill="x", side="bottom", padx=20, pady=20)

        self.btn_save = self.create_button(btn_fr, "⚡ Save Contact", GREEN, self.save_contact)
        self.btn_save.pack(side="right", padx=(10, 0))

        self.btn_clear = self.create_button(btn_fr, "Clear / New", BTN_BG, self.clear_form)
        self.btn_clear.pack(side="right")

        self.btn_del = self.create_button(btn_fr, "🗑 Delete", RED_C, self.delete_contact)
        self.btn_del.pack(side="left")
        self.btn_del.pack_forget()  # Hide initially

    def create_button(self, parent, text, color, command):
        # Creates a flat, colored label imitating a button (for better styling)
        btn = tk.Label(parent, text=text, bg=color, fg=BG if color != BTN_BG else TEXT, 
                       font=self.f_btn, relief="flat", cursor="hand2", padx=14, pady=8)
        
        # Determine hover color
        hover = BTN_HOV if color == BTN_BG else PANEL 
        if color == GREEN: hover = "#16A34A"
        elif color == RED_C: hover = "#DC2626"

        btn.bind("<Enter>", lambda e, b=btn, c=hover: b.configure(bg=c))
        btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=c))
        btn.bind("<Button-1>", lambda e: command())
        return btn

    # ── LOGIC ──────────────────────────────────────────────────────────────
    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {}
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_data(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(self.contacts, f, indent=4)
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save contacts: {e}")

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        query = self.search_var.get().lower()
        
        # Create an ordered list to keep track of IDs matching the listbox index
        self.filtered_ids = []
        
        for cid, data in self.contacts.items():
            name = data.get("name", "")
            phone = data.get("phone", "")
            if query in name.lower() or query in phone.lower():
                display_text = f"{name}  ({phone})"
                self.listbox.insert(tk.END, display_text)
                self.filtered_ids.append(cid)

    def on_select(self, event):
        selection = self.listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        cid = self.filtered_ids[index]
        self.current_selected_id = cid
        data = self.contacts[cid]

        # Populate form
        self.vars["name"].set(data.get("name", ""))
        self.vars["phone"].set(data.get("phone", ""))
        self.vars["email"].set(data.get("email", ""))
        self.vars["address"].set(data.get("address", ""))

        self.lbl_form_title.config(text="Edit Contact")
        self.btn_save.config(text="Update Contact")
        self.btn_del.pack(side="left")

    def clear_form(self):
        self.current_selected_id = None
        for var in self.vars.values():
            var.set("")
        
        self.listbox.selection_clear(0, tk.END)
        self.lbl_form_title.config(text="New Contact")
        self.btn_save.config(text="⚡ Save Contact")
        self.btn_del.pack_forget()

    def save_contact(self):
        import re
        name = self.vars["name"].get().strip()
        phone = self.vars["phone"].get().strip()
        email = self.vars["email"].get().strip()
        address = self.vars["address"].get().strip()

        # 1. Required fields
        if not name or not phone:
            messagebox.showwarning("Validation", "Name and Phone are required fields.")
            return

        # 2. Name validation: Only letters and spaces
        if not re.match(r"^[A-Za-z\s\-\']+$", name):
            messagebox.showwarning("Validation", "Name should only contain letters, spaces, hyphens, or apostrophes.")
            return

        # 3. Phone validation: Strict country-wise validation using 'phonenumbers'
        try:
            import phonenumbers
            # Default to checking against Indian rules ("IN") if no country code is present.
            # If the user types a country code (like +1 or +44), it will override this default and parse correctly.
            parsed_phone = phonenumbers.parse(phone, "IN")
            
            if not phonenumbers.is_valid_number(parsed_phone):
                messagebox.showwarning("Validation", "The phone number is structurally invalid for its country code.")
                return
            
            # Format nicely before saving (e.g., '+91 98765 43210')
            phone = phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            
        except ImportError:
            # Fallback if the library fails to load
            digits_only = re.sub(r"\D", "", phone)
            if len(digits_only) < 10 or len(digits_only) > 15:
                messagebox.showwarning("Validation", "Phone number must contain between 10 and 15 digits.")
                return
        except phonenumbers.phonenumberutil.NumberParseException:
            messagebox.showwarning("Validation", "The phone number format could not be parsed.")
            return

        # 4. Email validation: If provided, must have @ and . (basic sanity check)
        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            messagebox.showwarning("Validation", "Please provide a valid email address.")
            return

        # 5. Address validation: If provided, should be descriptive
        if address and len(address) < 10:
            messagebox.showwarning("Validation", "Please provide a more specific address (e.g. including street or city).")
            return

        cid = self.current_selected_id
        if not cid:
            cid = str(uuid.uuid4())

        self.contacts[cid] = {
            "name": name,
            "phone": phone,
            "email": email,
            "address": address
        }

        self.save_data()
        self.refresh_list()
        
        # Re-select the saved item
        try:
            idx = self.filtered_ids.index(cid)
            self.listbox.selection_set(idx)
            self.on_select(None)
        except ValueError:
            self.clear_form()

        messagebox.showinfo("Success", f"Contact '{name}' saved successfully.")

    def delete_contact(self):
        if not self.current_selected_id:
            return
        
        name = self.vars["name"].get()
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete {name}?")
        if confirm:
            del self.contacts[self.current_selected_id]
            self.save_data()
            self.refresh_list()
            self.clear_form()

if __name__ == "__main__":
    app = ContactBook()
    app.mainloop()
