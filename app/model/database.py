"""
=============================================================
  NepMart B2B Marketplace — Database Layer
=============================================================
  Auto-creates database + all 8 tables on first run.
  Runs ALTER TABLE migrations if columns are missing.
=============================================================
"""

import pymysql
import config


class Database:
    """Thin wrapper around a PyMySQL connection."""

    def __init__(self):
        # Bootstrap: create DB if it doesn't exist
        try:
            boot = pymysql.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                cursorclass=pymysql.cursors.DictCursor,
            )
            with boot.cursor() as cur:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{config.MYSQL_DATABASE}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            boot.commit()
            boot.close()
        except pymysql.MySQLError as e:
            print(f"[DB] Bootstrap warning: {e}")

        try:
            self.__connection = pymysql.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor,
                charset="utf8mb4",
            )
        except pymysql.MySQLError as e:
            print(f"[DB] Connection failed: {e}")
            raise

    # ── Query helpers ────────────────────────────────────────────

    def fetch_one(self, query, params=None):
        with self.__connection.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()

    def fetch_all(self, query, params=None):
        with self.__connection.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def execute(self, query, params=None):
        with self.__connection.cursor() as cur:
            cur.execute(query, params)
        self.__connection.commit()

    def execute_returning_id(self, query, params=None):
        with self.__connection.cursor() as cur:
            cur.execute(query, params)
            last_id = cur.lastrowid
        self.__connection.commit()
        return last_id

    def close(self):
        try:
            self.__connection.close()
        except Exception:
            pass

    # ── Schema bootstrap ─────────────────────────────────────────

    @staticmethod
    def create_tables():
        """Create all tables and run any ALTER migrations. Safe to call on every startup."""
        db = Database()

        # ── TABLE: users ────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INT AUTO_INCREMENT PRIMARY KEY,
                full_name     VARCHAR(150) NOT NULL,
                email         VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role          ENUM('buyer','seller','admin') NOT NULL DEFAULT 'buyer',
                phone_number  VARCHAR(30),
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── TABLE: sellers ──────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS sellers (
                seller_id                   INT AUTO_INCREMENT PRIMARY KEY,
                user_id                     INT NOT NULL UNIQUE,
                company_name                VARCHAR(200) NOT NULL,
                company_type                VARCHAR(100),
                whatsapp_number             VARCHAR(30),
                business_phone              VARCHAR(30),
                company_description         TEXT,
                business_address            TEXT,
                company_logo                VARCHAR(255),
                business_registration_number VARCHAR(100),
                created_at                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── TABLE: products ─────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id   INT AUTO_INCREMENT PRIMARY KEY,
                seller_id    INT NOT NULL,
                name         VARCHAR(255) NOT NULL,
                category     VARCHAR(100) NOT NULL,
                description  TEXT,
                price        DECIMAL(12,2) NOT NULL DEFAULT 0.00,
                stock        INT NOT NULL DEFAULT 0,
                image_path   VARCHAR(255),
                status       ENUM('active','inactive','out_of_stock') NOT NULL DEFAULT 'active',
                is_active    TINYINT(1) NOT NULL DEFAULT 1,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── TABLE: orders ───────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id         INT AUTO_INCREMENT PRIMARY KEY,
                buyer_id         INT NOT NULL,
                seller_id        INT,
                product_id       INT NOT NULL,
                quantity         INT NOT NULL DEFAULT 1,
                total_amount     DECIMAL(12,2) NOT NULL,
                order_status     ENUM('pending','confirmed','processing','shipped','delivered','cancelled')
                                 NOT NULL DEFAULT 'pending',
                seller_notes     TEXT,
                tracking_number  VARCHAR(100),
                created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (buyer_id)   REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── TABLE: cart ─────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS cart (
                cart_id    INT AUTO_INCREMENT PRIMARY KEY,
                user_id    INT NOT NULL,
                product_id INT NOT NULL,
                quantity   INT NOT NULL DEFAULT 1,
                added_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_cart_item (user_id, product_id),
                FOREIGN KEY (user_id)    REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── TABLE: search_history ───────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                history_id  INT AUTO_INCREMENT PRIMARY KEY,
                user_id     INT NOT NULL,
                search_term VARCHAR(255) NOT NULL,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── TABLE: view_history ─────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS view_history (
                history_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id    INT NOT NULL,
                product_id INT NOT NULL,
                viewed_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id)    REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── TABLE: recommendations ──────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id           INT NOT NULL,
                product_id        INT NOT NULL,
                recommendation_score FLOAT NOT NULL DEFAULT 0.0,
                UNIQUE KEY unique_rec (user_id, product_id),
                FOREIGN KEY (user_id)    REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── ALTER TABLE migrations (add missing columns) ─────────
        Database._run_migrations(db)

        # ── Default admin ────────────────────────────────────────
        admin = db.fetch_one("SELECT id FROM users WHERE email = %s", ("admin@nepmart.com",))
        if not admin:
            from werkzeug.security import generate_password_hash
            db.execute(
                "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s,%s,%s,%s)",
                ("NepMart Admin", "admin@nepmart.com", generate_password_hash("admin123"), "admin"),
            )
            print("[DB] Default admin created: admin@nepmart.com / admin123")

        print("[DB] All tables verified / created.")
        db.close()

    @staticmethod
    def _run_migrations(db):
        """Safely add any columns that may be missing in existing tables."""
        migrations = [
            # users
            ("users", "phone_number", "ALTER TABLE users ADD COLUMN phone_number VARCHAR(30) AFTER role"),
            # sellers
            ("sellers", "company_type",   "ALTER TABLE sellers ADD COLUMN company_type VARCHAR(100) AFTER company_name"),
            ("sellers", "company_description", "ALTER TABLE sellers ADD COLUMN company_description TEXT AFTER whatsapp_number"),
            ("sellers", "company_logo",    "ALTER TABLE sellers ADD COLUMN company_logo VARCHAR(255) AFTER business_address"),
            ("sellers", "business_registration_number", "ALTER TABLE sellers ADD COLUMN business_registration_number VARCHAR(100) AFTER company_logo"),
            ("sellers", "company_name",    "ALTER TABLE sellers ADD COLUMN company_name VARCHAR(200) NOT NULL DEFAULT '' AFTER user_id"),
            # products
            ("products", "image_path",  "ALTER TABLE products ADD COLUMN image_path VARCHAR(255) AFTER stock"),
            ("products", "status",      "ALTER TABLE products ADD COLUMN status ENUM('active','inactive','out_of_stock') NOT NULL DEFAULT 'active' AFTER image_path"),
            ("products", "updated_at",  "ALTER TABLE products ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP AFTER created_at"),
            # orders
            ("orders", "seller_id",        "ALTER TABLE orders ADD COLUMN seller_id INT AFTER buyer_id"),
            ("orders", "seller_notes",     "ALTER TABLE orders ADD COLUMN seller_notes TEXT AFTER order_status"),
            ("orders", "tracking_number",  "ALTER TABLE orders ADD COLUMN tracking_number VARCHAR(100) AFTER seller_notes"),
            ("orders", "order_status",     None),  # already exists if table was created fresh
        ]

        for table, column, alter_sql in migrations:
            if alter_sql is None:
                continue
            try:
                exists = db.fetch_one(
                    "SELECT 1 FROM information_schema.COLUMNS "
                    "WHERE TABLE_SCHEMA=%s AND TABLE_NAME=%s AND COLUMN_NAME=%s",
                    (config.MYSQL_DATABASE, table, column)
                )
                if not exists:
                    db.execute(alter_sql)
                    print(f"[DB] Migration: Added {table}.{column}")
            except Exception as e:
                print(f"[DB] Migration warning ({table}.{column}): {e}")