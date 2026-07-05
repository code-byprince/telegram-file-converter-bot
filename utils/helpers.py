import os
import uuid
import shutil
from config import TEMP_DIR, MAX_FILE_SIZE_MB


def new_session_dir() -> str:
    """Har request ke liye alag temp folder banata hai, taaki files mix na ho."""
    session_id = str(uuid.uuid4())[:8]
    path = os.path.join(TEMP_DIR, session_id)
    os.makedirs(path, exist_ok=True)
    return path


def cleanup(path: str):
    """Session folder delete kar deta hai (input/output files hata ke)."""
    try:
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)
        elif os.path.isfile(path):
            os.remove(path)
    except Exception:
        pass


def get_extension(filename: str) -> str:
    return os.path.splitext(filename)[1].lower().lstrip(".")


def human_size(num_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f}{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f}TB"


def is_file_too_big(size_bytes: int) -> bool:
    return size_bytes > MAX_FILE_SIZE_MB * 1024 * 1024
