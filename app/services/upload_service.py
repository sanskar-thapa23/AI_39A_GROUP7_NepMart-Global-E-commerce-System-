"""
=============================================================
  NepMart — Upload Service
=============================================================
  Secure file upload handler for product images.
=============================================================
"""

import os
import uuid
import config


ALLOWED = config.ALLOWED_EXTENSIONS


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED
    )


def save_product_image(file_storage):
    """
    Validate and save an uploaded product image.

    Args:
        file_storage: werkzeug.datastructures.FileStorage object

    Returns:
        str: relative URL path like 'uploads/abc123.jpg'
             or None if no file / invalid type
    """
    if not file_storage or file_storage.filename == "":
        return None

    if not allowed_file(file_storage.filename):
        return None

    ext      = file_storage.filename.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{ext}"

    upload_dir = config.UPLOAD_FOLDER
    os.makedirs(upload_dir, exist_ok=True)

    file_storage.save(os.path.join(upload_dir, filename))
    return f"uploads/{filename}"


def delete_product_image(image_path):
    """Delete an old product image from disk."""
    if not image_path:
        return
    full = os.path.join(
        os.path.dirname(__file__), "..", "static", image_path
    )
    full = os.path.normpath(full)
    if os.path.isfile(full):
        os.remove(full)
