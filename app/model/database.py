import pymysql
import config

class Database:
    def __init__(self):
        """Open a database connection when object is created."""
        try:
            self.__connection = pymysql.connect(
                host=config.MYSQL_HOST,
                user=config.MYSQL_USER,
                password=config.MYSQL_PASSWORD,
                database=config.MYSQL_DATABASE,
                cursorclass=pymysql.cursors.DictCursor,
            )
            print("Database connected successfully!")
        except pymysql.MySQLError as e:
            print("Database connection failed!")
            print("Error:", e)
 
    def fetch_one(self, query, params=None):
        """Run a query and return ONE result (or None)."""
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        result = cursor.fetchone()
        cursor.close()
        return result

    def fetch_all(self, query, params=None):
        """Run a query and return ALL results as a list."""
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        return list(results)

    def execute(self, query, params=None):
        """Run a query that changes data (INSERT, UPDATE, DELETE)."""
        cursor = self.__connection.cursor()
        cursor.execute(query, params)
        self.__connection.commit()
        cursor.close()

    def close(self):
        """Close the database connection."""
        self.__connection.close()

    # ── Static Method: Create tables on app startup ─────────

    @staticmethod
    def create_tables():
        """
        Create database tables if they don't exist.
        Includes Many-to-Many structural mapping between Users and Products.
        """
        db = Database()
        
        # 1. USERS TABLE (Checked mapping configuration fields)
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(100) NOT NULL UNIQUE,
                phone_number VARCHAR(20),
                password VARCHAR(255) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'customer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """) 

        # Migrations for existing users table
        try:
            db.execute("ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) NULL AFTER email")
        except Exception:
            pass

        # 2. PRODUCTS TABLE (Aligned with Product Model specifications)
        db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                vendor_id INT,
                product_image TEXT NOT NULL,
                product_name VARCHAR(255) NOT NULL,
                product_prices TEXT,
                product_price DECIMAL(10, 2) NOT NULL,
                stock INT DEFAULT 0,
                category VARCHAR(100),
                location VARCHAR(100),
                product_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vendor_id) REFERENCES users(id) ON DELETE SET NULL
            )
        """)

        # Migrations for existing products table
        try:
            db.execute("ALTER TABLE products ADD COLUMN vendor_id INT AFTER id")
            db.execute("ALTER TABLE products ADD CONSTRAINT fk_vendor FOREIGN KEY (vendor_id) REFERENCES users(id) ON DELETE SET NULL")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE products ADD COLUMN category VARCHAR(100) AFTER product_price")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE products ADD COLUMN location VARCHAR(100) AFTER category")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE products ADD COLUMN stock INT DEFAULT 0 AFTER product_price")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE products ADD CONSTRAINT fk_vendor FOREIGN KEY (vendor_id) REFERENCES users(id) ON DELETE SET NULL")
        except Exception:
            pass

        # 3. MANY-TO-MANY PIVOT TABLE (User <-> Product Mapping System)
        db.execute("""
            CREATE TABLE IF NOT EXISTS user_products (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_product (user_id, product_id)
            )
        """)

        # 4. COUPONS TABLE
        db.execute("""
            CREATE TABLE IF NOT EXISTS coupons (
                id INT AUTO_INCREMENT PRIMARY KEY,
                coupon_code VARCHAR(100) NOT NULL UNIQUE,
                discount_percentage INT NOT NULL,
                vendor_id INT NOT NULL,
                expires_at TIMESTAMP NOT NULL,
                created_by INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (vendor_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Migrations for existing coupons table
        try:
            db.execute("ALTER TABLE coupons ADD COLUMN vendor_id INT NOT NULL AFTER discount_percentage")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE coupons ADD COLUMN created_by INT NOT NULL AFTER vendor_id")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE coupons ADD CONSTRAINT fk_coupon_vendor FOREIGN KEY (vendor_id) REFERENCES users(id) ON DELETE CASCADE")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE coupons ADD CONSTRAINT fk_coupon_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE CASCADE")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE coupons ADD CONSTRAINT fk_coupon_vendor FOREIGN KEY (vendor_id) REFERENCES users(id) ON DELETE CASCADE")
        except Exception:
            pass

        # 5. ORDERS TABLE 
        db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT,
                total_amount DECIMAL(10, 2) NOT NULL,
                discount_amount DECIMAL(10, 2) DEFAULT 0,
                coupon_id INT NULL,
                coupon_code VARCHAR(100) NULL,
                status VARCHAR(50) NOT NULL DEFAULT 'pending',
                shipping_address TEXT,
                phone_number VARCHAR(20),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL,
                FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE SET NULL
            )
        """) 

        # Migrations for existing orders table
        try:
            db.execute("ALTER TABLE orders ADD COLUMN product_id INT AFTER user_id")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE orders ADD COLUMN discount_amount DECIMAL(10, 2) DEFAULT 0 AFTER total_amount")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE orders ADD COLUMN coupon_id INT NULL AFTER discount_amount")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE orders ADD COLUMN coupon_code VARCHAR(100) NULL AFTER coupon_id")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE orders ADD COLUMN shipping_address TEXT AFTER status")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE orders ADD COLUMN phone_number VARCHAR(20) AFTER shipping_address")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE orders ADD CONSTRAINT fk_order_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL")
        except Exception:
            pass

        try:
            db.execute("ALTER TABLE orders ADD CONSTRAINT fk_order_coupon FOREIGN KEY (coupon_id) REFERENCES coupons(id) ON DELETE SET NULL")
        except Exception:
            pass

        
        # 6. SHOPPING CART TABLE (Mapping User <-> Product with Quantity)
        db.execute("""
            CREATE TABLE IF NOT EXISTS shopping_cart (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                quantity INT NOT NULL DEFAULT 1,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_cart_product (user_id, product_id)
            )
        """)

        # 7. WISHLIST TABLE (Mapping User <-> Product)
        db.execute("""
            CREATE TABLE IF NOT EXISTS wishlist (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                product_id INT NOT NULL,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
                UNIQUE KEY unique_user_wishlist_product (user_id, product_id)
            )
        """)

        # 7. PRODUCT VIEWS TABLE (Tracking for Recommendations & Vendor Metrics)
        db.execute("""
            CREATE TABLE IF NOT EXISTS product_views (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NULL,
                product_id INT NOT NULL,
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)


        # Create default admin if not exists
        admin = db.fetch_one(
            "SELECT * FROM users WHERE email = %s", ("admin@admin.com",)
        )
        if not admin:
            from werkzeug.security import generate_password_hash

            db.execute(
                "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                ("Admin", "admin@admin.com", generate_password_hash("admin123"), "admin"),
            )

        db.close()