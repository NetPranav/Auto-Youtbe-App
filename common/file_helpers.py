import os
import shutil
from pathlib import Path

def ensure_directory(path_str: str) -> Path:
    """Ensure a directory exists, create it if it doesn't."""
    path = Path(path_str)
    path.mkdir(parents=True, exist_ok=True)
    return path

def delete_directory(path_str: str) -> None:
    """Safely delete a directory and all its contents."""
    path = Path(path_str)
    if path.exists() and path.is_dir():
        shutil.rmtree(path)

def file_exists(path_str: str) -> bool:
    """Check if a file exists."""
    return Path(path_str).is_file()
