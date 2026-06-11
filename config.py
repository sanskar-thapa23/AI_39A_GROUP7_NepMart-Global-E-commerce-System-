import os

# ── Core Security ─────────────────────────────────────────
SECRET_KEY = os.environ.get("SECRET_KEY", "nepmart-b2b-super-secret-key-2026!")

# ── MySQL Database ────────────────────────────────────────
MYSQL_HOST     = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER     = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "qlz@9766#")
MYSQL_DATABASE = os.environ.get("MYSQL_DATABASE", "nepmart")

# ── File Uploads ──────────────────────────────────────────
UPLOAD_FOLDER       = os.path.join(os.path.dirname(__file__), "app", "static", "uploads")
MAX_CONTENT_LENGTH  = 5 * 1024 * 1024   # 5 MB max upload
ALLOWED_EXTENSIONS  = {"jpg", "jpeg", "png", "gif", "webp"}

# ── WTForms / CSRF ───────────────────────────────────────
WTF_CSRF_ENABLED = True