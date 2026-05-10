from pathlib import Path
import shutil
from datetime import datetime
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk

class InboxHandler(FileSystemEventHandler):
    def __init__(self, inbox_folder, logger):
        self.inbox_folder = Path(inbox_folder)
        self.logger = logger
    def on_created(self, event):
        if event.is_directory:
            return
        
        file_path = Path(event.src_path)

        if not is_file_complete(file_path):
            self.logger(f"skipped incompleted file: {file_path.name}")
            return
        destination = move_file(file_path, self.inbox_folder)
        if destination:
            self.logger(f"moved file {file_path.name} to  {destination}")

def startWatcher(inbox_folder, logger):
    handler = InboxHandler(inbox_folder, logger)
    observer = Observer()
    observer.schedule(handler, str(Path(inbox_folder)), recursive=False)
    observer.start()
    return observer

def stop_watcher(observer):
    if observer:
        observer.stop()
        observer.join()

def get_filecategory(file_path):
    suffix = Path(file_path).suffix.lower()

    if suffix in [".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"]:
        return "images"
    if suffix in [".pdf"]:
        return "pdfs"
    if suffix in [".mp4", ".mov", ".avi", ".mkv"]:
        return "videos"
    if suffix in [".txt", ".docx", ".doc", ".md"]:
        return "documents"
    if suffix in [".zip", ".rar", ".7z", ".tar", ".gz"]:
        return "archives"
    return "other"

def make_target_folder(base_folder, category):
    target_folder = Path(base_folder) /category
    target_folder.mkdir(parents=True, exist_ok=True)
    return target_folder

def createSafeDestination(target_folder, file_name):
    destination = Path(target_folder)/file_name

    if not destination.exists():
        return destination
    stem = destination.stem
    suffix = destination.suffix
    counter = 1

    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_destination = Path(target_folder) / new_name
        if not new_destination.exists():
            return new_destination
        counter += 1
        
def move_file(file_path, inbox_folder):
    file_path = Path(file_path)
    if not file_path.is_file():
        return None
    category = get_filecategory(file_path)
    target_folder = make_target_folder(inbox_folder, category)
    destination = createSafeDestination(target_folder, file_path.name)
    shutil.move(str(file_path), str(destination))
    return destination

def log_action(message, log_file="log.log"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"
    
    with open(log_file, "a", encoding= "utf-8") as file:
        file.write(line)

def process_current_file(inbox_folder):
    inbox_folder = Path(inbox_folder)
    for item in inbox_folder.iterdir():
        if item.is_file():
            destination = move_file(item, inbox_folder)
            if destination:
                log_action(f"file {item.name} to {destination}")

def new_file(file_path, inbox_folder):
    file_path = Path(file_path)

    if not file_path.exists():
        return
    time.sleep(1)
    destination =move_file(file_path, inbox_folder)
    if destination:
        log_action(f"file {file_path.name} to {destination}")

def is_file_complete(path, stable_seconds=2, timeout=30):
    path = Path(path)
    start = time.time()
    last_size = -1
    while time.time() - start < timeout:
        if not path.exists():
            return False
        size = path.stat().st_size
        if size == last_size:
            
            stable_start = time.time()
            while time.time() - stable_start < stable_seconds:
                time.sleep(0.5)
                if not path.exists():
                    return False
                if path.stat().st_size != size:
                        last_size = path.stat().st_size
                        break
            else:
                return True
        last_size = size
        time.sleep(0.5)
    return False

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("sorta")
        self.root.geometry("860x560")
        self.root.minsize(400, 300)
        self.root.configure(bg="#f5f6fa")

        self.bg = "#f5f6fa"
        self.card = "white"
        self.text = "#1f2937"
        self.muted = "#6b7280"
        self.accent = "#16acf2"
        self.success = "#13aa4b"
        self.danger = "#da1e1e"
        self.border = "#dedfe2"

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("Shell.TFrame", background=self.bg)
        self.style.configure("Card.TFrame", background=self.card, borderwidth=1, relief="solid")
        self.style.configure("Title.TLabel", background=self.bg, foreground=self.text)
        self.style.configure("Sub.TLabel", background=self.bg, foreground=self.muted)
        self.style.configure("CardLabel.TLabel", background=self.card, foreground=self.text)
        self.style.configure("Primary.TButton", foreground="white", background=self.accent, padding=(12,6))
        self.style.map("Primary.TButton", background=[("active", "#1198e0"), ("disabled", "#a3a8b2")])
        self.style.configure("Secondary.TButton", foreground=self.text, background="#e9e9eb", padding=(12, 6))
        self.style.map("Secondary.TButton", background=[("active", "#d1d5db"), ("disabled", "#f8f9fa")])

        self.observer = None
        self.log_file = "log.log"

        self.folder_var = tk.StringVar(value=str(Path("inbox").resolve()))
        shell = ttk.Frame(root, style="Shell.TFrame", padding=16)
        shell.pack(fill="both", expand=True)

        ttk.Label(shell, text="sorta", style="Title.TLabel").pack(anchor="w")
        ttk.Label(shell, text="short all the junk in your download folder ;/", style="Sub.TLabel").pack(anchor="w", pady=(0, 12))

        card = ttk.Frame(shell, style="Card.TFrame", padding=14)
        card.pack(fill="x", pady=(0, 12))

        ttk.Label(card, text="folder", style="CardLabel.TLabel").pack(anchor="w")

        row = ttk.Frame(card, style="Card.TFrame")
        row.pack(fill="x", pady=(6, 0))

        self.folder_entry = ttk.Entry(row, textvariable=self.folder_var)
        self.folder_entry.pack(side="left", fill="x", expand=True)

        ttk.Button(row, text="Browse", command=self.browse_folder, style="Secondary.TButton").pack(side="left", padx=(8,0))

        control = ttk.Frame(shell, style="Shell.TFrame")
        control.pack(fill="x", pady=(0, 10))
        
        self.start_button = ttk.Button(control, text="start", command=self.start_clicked, style="Primary.TButton")
        self.start_button.pack(side="left")
        self.stop_button = ttk.Button(control, text="stop", command=self.stop_clicked, state="disabled", style="Secondary.TButton")
        self.stop_button.pack(side="left", padx=8)

        self.status_label = ttk.Label(control, text="idling ... .", bg=self.bg, fg=self.muted, padx=10,)
        self.status_label.pack(side="left", padx=12)
        self.log_box = scrolledtext.ScrolledText(shell, height=18, bg="white", fg=self.text, insertbackground=self.text, relief="flat", borderwidth=1, padx=10, pady=10)
        self.log_box.pack(fill="both", expand=True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def log(self, message):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{ts}] {message}"
        self.log_box.insert(tk.END, line + "\n")
        self.log_box.see(tk.END)
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def process_existing_files(self, inbox_folder):
        inbox_folder = Path(inbox_folder)
        inbox_folder.mkdir(parents=True, exist_ok=True)
        for item in inbox_folder.iterdir():
            if item.is_file():
                destination = move_file(item, inbox_folder)
                if destination:
                    self.log(f"moved {item.name} to {destination}")

    def start_clicked(self):
        if self.observer is not None:
            messagebox.showinfo("Runnning", "watcher already running")
            return
        
        folder = Path(self.folder_var.get()).expanduser()
        folder.mkdir(parents=True, exist_ok=True)

        self.process_existing_files(folder)
        self.observer = startWatcher(folder, self.log)

        self.status_var.set(f"watching {folder}")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.log(f"started watching {folder}")

    def stop_clicked(self):
        if self.observer is None:
            return
        stop_watcher(self.observer)
        self.observer = None
        self.status_var.set("status: stopped")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.log("Stopped watching.")

    def on_close(self):
        if self.observer is not None:
            self.stop_clicked()
        self.root.destroy()
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()