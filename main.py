from pathlib import Path
import shutil
from datetime import datetime
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class InboxHandler(FileSystemEventHandler):
    def __init__(self, inbox_folder):
        self.inbox_folder = inbox_folder
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

def new_file(file_path, inbox_folder):
    file_path = Path(file_path)
    if not file_path.exists():
        return
    if not is_file_complete(file_path):
        log_action(f"skipped incomplete file {file_path.name}")
        return
    destination = move_file(file_path, inbox_folder)
    if destination:
        log_action(f"file moved {file_path.name} to {destination}")