from pathlib import Path

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