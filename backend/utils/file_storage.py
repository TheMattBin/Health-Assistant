import os
import uuid
from datetime import datetime
from typing import Optional

UPLOADS_DIR = "uploads"
USERS_DIR = os.path.join(UPLOADS_DIR, "users")

def ensure_user_upload_dir(user_id: str) -> str:
    """Create and return user-specific upload directory"""
    user_dir = os.path.join(USERS_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)
    return user_dir

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename preserving extension"""
    if not original_filename:
        return f"{uuid.uuid4()}.file"

    name, ext = os.path.splitext(original_filename)
    if not ext:
        ext = ".file"

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"{timestamp}_{unique_id}{ext}"

def save_uploaded_file(file_content: bytes, user_id: str, original_filename: str) -> str:
    """Save uploaded file and return relative file path"""
    user_dir = ensure_user_upload_dir(user_id)
    filename = generate_unique_filename(original_filename)
    file_path = os.path.join(user_dir, filename)

    with open(file_path, "wb") as f:
        f.write(file_content)

    # Return relative path from backend root
    return os.path.join(USERS_DIR, user_id, filename).replace("\\", "/")

def get_file_url(file_path: str) -> str:
    """Get URL to access the file"""
    if not file_path:
        return None
    return f"/{file_path}"

def delete_file(file_path: str) -> bool:
    """Delete file if it exists"""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception:
        pass
    return False

def cleanup_user_files(user_id: str, keep_files: list = None) -> int:
    """Delete user files not in keep_files list, return count of deleted files"""
    if keep_files is None:
        keep_files = []

    user_dir = os.path.join(USERS_DIR, user_id)
    if not os.path.exists(user_dir):
        return 0

    deleted_count = 0
    for filename in os.listdir(user_dir):
        file_path = os.path.join(user_dir, filename)
        relative_path = os.path.join(USERS_DIR, user_id, filename).replace("\\", "/")

        if relative_path not in keep_files and os.path.isfile(file_path):
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception:
                pass

    return deleted_count