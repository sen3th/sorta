from pathlib import Path
import shutil
from datetime import datetime
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class InboxHandler(FileSystemEventHandler):
    def __init__(self, inbox_folder):
        self.inbox_folder = inbox_folder
    def on_created(self, event):
        if not event.is_directory:
            new_file(event.src_path, self.inbox_folder)

def startWatcher(inbox_folder):
    inbox_folder = Path(inbox_folder)
    handler = InboxHandler(inbox_folder)
    observer = Observer()
    observer.schedule(handler, str(inbox_folder), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop() 

    observer.join()

def get_filecategory(file_path):
    suffix = Path(file_path).suffix.lower()

    if suffix in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        return "images"
    if suffix in [".pdf"]:
        return "pdfs"
    if suffix in [".mp4"]:
        return "videos"
    if suffix in [".txt", ".docx"]:
        return "documents"
    if suffix in [".zip"]:
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

if __name__ == "__main__":
    inbox_folder = Path("inbox")
    inbox_folder.mkdir(exist_ok=True)
    process_current_file(inbox_folder)
    startWatcher(inbox_folder)