"""
=============================================================
  NepMart B2B Marketplace — Database Layer
=============================================================
  Manages PyMySQL connection lifecycle and provides
  helper methods used by all model classes.
  Auto-creates all required tables on first run.
=============================================================
"""

import pymysql
import config


class Database:
    """Thin wrapper around a PyMySQL connection."""

    def __init__(self):
        """Open a database connection, auto-creating the DB if needed."""
        try:
            # First connect WITHOUT specifying a database so we can CREATE it
            bootstrap = pymysql.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                cursorclass=pymysql.cursors.DictCursor,
            )
            with bootstrap.cursor() as cur:
                cur.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{config.MYSQL_DATABASE}` "
                    "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
                )
            bootstrap.commit()
            bootstrap.close()
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
            print("[DB] Connected successfully.")
        except pymysql.MySQLError as e:
            print(f"[DB] Connection failed: {e}")
            raise

    # ── Query Helpers ────────────────────────────────────────────

    def fetch_one(self, query, params=None):
        """Execute a SELECT and return the first row as a dict, or None."""
        with self.__connection.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()

    def fetch_all(self, query, params=None):
        """Execute a SELECT and return all rows as a list of dicts."""
        with self.__connection.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()

    def execute(self, query, params=None):
        """Execute a data-modifying query (INSERT / UPDATE / DELETE)."""
        with self.__connection.cursor() as cur:
            cur.execute(query, params)
        self.__connection.commit()

    def execute_returning_id(self, query, params=None):
        """Execute an INSERT and return the new row's auto-increment ID."""
        with self.__connection.cursor() as cur:
            cur.execute(query, params)
            last_id = cur.lastrowid
        self.__connection.commit()
        return last_id

    def close(self):
        """Close the underlying connection."""
        try:
            self.__connection.close()
        except Exception:
            pass

    # ── Schema Bootstrap ────────────────────────────────────────

    @staticmethod
    def create_tables():
        """
        Auto-create every table NepMart needs.
        Safe to call on every startup (IF NOT EXISTS).
        """
        db = Database()

        # ── users ──────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INT AUTO_INCREMENT PRIMARY KEY,
                full_name     VARCHAR(150) NOT NULL,
                email         VARCHAR(150) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                role          ENUM('buyer','seller','admin') NOT NULL DEFAULT 'buyer',
                phone         VARCHAR(20),
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── sellers ─────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS sellers (
                seller_id        INT AUTO_INCREMENT PRIMARY KEY,
                user_id          INT NOT NULL UNIQUE,
                business_name    VARCHAR(200) NOT NULL,
                whatsapp_number  VARCHAR(30),
                business_phone   VARCHAR(30),
                business_address TEXT,
                created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── products ────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                product_id   INT AUTO_INCREMENT PRIMARY KEY,
                seller_id    INT NOT NULL,
                name         VARCHAR(255) NOT NULL,
                category     VARCHAR(100) NOT NULL,
                description  TEXT,
                price        DECIMAL(12,2) NOT NULL DEFAULT 0.00,
                stock        INT NOT NULL DEFAULT 0,
                image        VARCHAR(255),
                is_active    TINYINT(1) NOT NULL DEFAULT 1,
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (seller_id) REFERENCES sellers(seller_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── orders ──────────────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id     INT AUTO_INCREMENT PRIMARY KEY,
                buyer_id     INT NOT NULL,
                product_id   INT NOT NULL,
                quantity     INT NOT NULL DEFAULT 1,
                total_amount DECIMAL(12,2) NOT NULL,
                order_status ENUM('pending','confirmed','shipped','delivered','cancelled')
                             NOT NULL DEFAULT 'pending',
                created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (buyer_id)   REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── cart ────────────────────────────────────────────────
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

        # ── search_history ──────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS search_history (
                history_id  INT AUTO_INCREMENT PRIMARY KEY,
                user_id     INT NOT NULL,
                search_term VARCHAR(255) NOT NULL,
                searched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── view_history ────────────────────────────────────────
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

        # ── recommendations ─────────────────────────────────────
        db.execute("""
            CREATE TABLE IF NOT EXISTS recommendations (
                recommendation_id INT AUTO_INCREMENT PRIMARY KEY,
                user_id           INT NOT NULL,
                product_id        INT NOT NULL,
                score             FLOAT NOT NULL DEFAULT 0.0,
                UNIQUE KEY unique_rec (user_id, product_id),
                FOREIGN KEY (user_id)    REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)

        # ── Default admin account ───────────────────────────────
        admin = db.fetch_one("SELECT id FROM users WHERE email = %s", ("admin@nepmart.com",))
        if not admin:
            from werkzeug.security import generate_password_hash
            db.execute(
                "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                ("NepMart Admin", "admin@nepmart.com", generate_password_hash("admin123"), "admin"),
            )
            print("[DB] Default admin created: admin@nepmart.com / admin123")

        print("[DB] All tables verified / created.")
        db.close()