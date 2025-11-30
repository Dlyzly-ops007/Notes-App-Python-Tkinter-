import os
import tkinter as tk
from tkinter import messagebox, ttk

NOTES_DIR = "notes"

def ensure_notes_dir():
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)

def get_note_path(title):
    #Title names(from "notes" folder)
    safe_title = "".join(c for c in title if c not in '\\/:*?"<>|').strip()
    if not safe_title:
        return None
    return os.path.join(NOTES_DIR, safe_title + ".txt")

class NotesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Notes App")
        self.root.geometry("900x550")

        ensure_notes_dir()

        # Autosave state
        self.autosave_enabled = tk.BooleanVar(value=False)
        self.autosave_interval = tk.IntVar(value=30) #value is default

        self.create_widgets()
        self.load_notes_list()

        # Start autosave loop (it will only act if toggle is ON)
        self.schedule_autosave()

    def create_widgets(self):
        # Main layout: left = listbox, right = editor
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # LEFT SIDE (notes list + search) 
        left_frame = ttk.Frame(self.root, padding=10)
        left_frame.grid(row=0, column=0, sticky="ns")
        left_frame.rowconfigure(2, weight=1)
        lbl_notes = ttk.Label(left_frame, text="Notes")
        lbl_notes.grid(row=0, column=0, sticky="w")

        # Search bar
        search_frame = ttk.Frame(left_frame)
        search_frame.grid(row=1, column=0, pady=(5, 5), sticky="ew")
        search_frame.columnconfigure(0, weight=1)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        btn_search = ttk.Button(search_frame, text="Search", command=self.search_notes)
        btn_search.grid(row=0, column=1, padx=(0, 5))
        btn_clear = ttk.Button(search_frame, text="Clear", command=self.clear_search)
        btn_clear.grid(row=0, column=2)

        # Notes listbox
        self.notes_listbox = tk.Listbox(left_frame, height=20, width=30)
        self.notes_listbox.grid(row=2, column=0, sticky="ns")
        self.notes_listbox.bind("<<ListboxSelect>>", self.on_note_select)
        btn_refresh = ttk.Button(left_frame, text="Refresh", command=self.load_notes_list)
        btn_refresh.grid(row=3, column=0, pady=(5, 0), sticky="ew")

        #RIGHT SIDE (editor)
        right_frame = ttk.Frame(self.root, padding=10)
        right_frame.grid(row=0, column=1, sticky="nsew")
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(3, weight=1)
        lbl_title = ttk.Label(right_frame, text="Title:")
        lbl_title.grid(row=0, column=0, sticky="w")
        self.title_entry = ttk.Entry(right_frame)
        self.title_entry.grid(row=1, column=0, sticky="ew", pady=5)
        lbl_content = ttk.Label(right_frame, text="Content:")
        lbl_content.grid(row=2, column=0, sticky="w")
        self.text_area = tk.Text(right_frame, wrap="word")
        self.text_area.grid(row=3, column=0, sticky="nsew", pady=5)

        #BOTTOM BUTTON (buttons + autosave)
        bottom_frame = ttk.Frame(right_frame)
        bottom_frame.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)
        bottom_frame.columnconfigure(1, weight=1)
        bottom_frame.columnconfigure(2, weight=1)
        bottom_frame.columnconfigure(3, weight=1)
        bottom_frame.columnconfigure(4, weight=1)
        btn_new = ttk.Button(bottom_frame, text="New", command=self.new_note)
        btn_new.grid(row=0, column=0, padx=5, sticky="ew")
        btn_save = ttk.Button(bottom_frame, text="Save", command=self.save_note)
        btn_save.grid(row=0, column=1, padx=5, sticky="ew")
        btn_delete = ttk.Button(bottom_frame, text="Delete", command=self.delete_note)
        btn_delete.grid(row=0, column=2, padx=5, sticky="ew")
        
        #Autosave toggle
        autosave_check = ttk.Checkbutton(
            bottom_frame,
            text="Autosave",
            variable=self.autosave_enabled
        )
        autosave_check.grid(row=0, column=3, padx=5, sticky="w")
        #Selector
        interval_frame = ttk.Frame(bottom_frame)
        interval_frame.grid(row=0, column=4, sticky="e", padx=5)

        ttk.Label(interval_frame, text="Every").grid(row=0, column=0)
        interval_spin = ttk.Spinbox(
            interval_frame,
            from_=5,
            to=300,
            textvariable=self.autosave_interval,
            width=5
        )
        interval_spin.grid(row=0, column=1, padx=3)
        ttk.Label(interval_frame, text="sec").grid(row=0, column=2)

    #NOTE LIST / FILE HANDLING
    def load_notes_list(self):
        self.notes_listbox.delete(0, tk.END)
        ensure_notes_dir()
        files = [f for f in os.listdir(NOTES_DIR) if f.endswith(".txt")]
        files.sort()

        for f in files:
            title = os.path.splitext(f)[0]
            self.notes_listbox.insert(tk.END, title)

    def on_note_select(self, event):
        selection = self.notes_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        title = self.notes_listbox.get(index)
        path = get_note_path(title)
        if not path or not os.path.exists(path):
            return

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Load into editor
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, title)

        self.text_area.delete("1.0", tk.END)
        self.text_area.insert(tk.END, content)

    def new_note(self):
        self.title_entry.delete(0, tk.END)
        self.text_area.delete("1.0", tk.END)
        self.notes_listbox.selection_clear(0, tk.END)

    def save_note(self):
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("No title", "Please enter a title for the note.")
            return

        path = get_note_path(title)
        if path is None:
            messagebox.showerror("Invalid title", "Title contains invalid characters.")
            return

        content = self.text_area.get("1.0", tk.END).rstrip()

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        self.load_notes_list()
        messagebox.showinfo("Saved", f"Note '{title}' saved successfully.")

    def delete_note(self):
        selection = self.notes_listbox.curselection()
        if not selection:
            messagebox.showwarning("No selection", "Select a note to delete.")
            return

        index = selection[0]
        title = self.notes_listbox.get(index)
        path = get_note_path(title)

        if not path or not os.path.exists(path):
            messagebox.showerror("Error", "File not found.")
            return

        confirm = messagebox.askyesno("Delete", f"Are you sure you want to delete '{title}'?")
        if not confirm:
            return

        os.remove(path)
        self.new_note()
        self.load_notes_list()
        messagebox.showinfo("Deleted", f"Note '{title}' deleted.")

    #SEARCH 
    def search_notes(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.load_notes_list()
            return

        ensure_notes_dir()
        files = [f for f in os.listdir(NOTES_DIR) if f.endswith(".txt")]

        matches = []

        for f in files:
            title = os.path.splitext(f)[0]
            path = os.path.join(NOTES_DIR, f)

            try:
                with open(path, "r", encoding="utf-8") as file_obj:
                    content = file_obj.read().lower()
            except Exception:
                content = ""

            # Match if query in title OR in content
            if query in title.lower() or query in content:
                matches.append(title)

        # Update listbox with matches
        self.notes_listbox.delete(0, tk.END)
        for title in sorted(matches):
            self.notes_listbox.insert(tk.END, title)

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.load_notes_list()

    #AUTOSAVE

    def schedule_autosave(self):
        """Schedule the autosave loop to run periodically."""
        #Call autosave_loop after interval seconds
        interval_ms = max(5, self.autosave_interval.get()) * 1000
        self.root.after(interval_ms, self.autosave_loop)

    def autosave_loop(self):
        """Called periodically. If autosave is enabled, saves current note silently."""
        if self.autosave_enabled.get():
            self.autosave_current_note()

        #Reschedule next autosave
        self.schedule_autosave()

    def autosave_current_note(self):
        title = self.title_entry.get().strip()
        if not title:
            #No title -> nothing to autosave
            return
        path = get_note_path(title)
        if path is None:
            return
        content = self.text_area.get("1.0", tk.END).rstrip()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            print(f"Autosave error: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = NotesApp(root)
    root.mainloop()
