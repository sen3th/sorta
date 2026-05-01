from pathlib import Path
import shutil
from datetime import datetime

def get_filecategory(file_path):
    suffix = Path(file_path).suffix.lower()

    if suffix in [".jpg", "jpeg", ".png", ".gif", "webp"]:
        return "images"
    if suffix in [".pdf"]:
        return "pdfs"
    if suffix in ["mp4"]:
        return "videos"
    if suffix in [".txt", "docx"]:
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

def process_current_file(inbox_folder):
    inbox_folder = Path(inbox_folder)
    for item in inbox_folder.iterdir():
        if item.is_file():
            destination = move_file(item, inbox_folder)