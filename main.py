from pathlib import Path

def get_filecategory(file_path):
    suffix = Path(file_path).suffix.lower()

    if suffix in [".jpg", "jpeg", ".png", ".gif", "webp"]:
        return "images"
    if suffix in [".pdf"]:
        return "pdfs"
