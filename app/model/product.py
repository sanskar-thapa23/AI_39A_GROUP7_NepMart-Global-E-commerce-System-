"""
=============================================================
  NepMart — Product Model
=============================================================
  Inherits BaseModel. Manages seller-owned products.
  Encapsulates price validation.
=============================================================
"""

from app.model.basemodel import BaseModel
from .database import Database


class Product(BaseModel):

    @property
    def table(self):
        return "products"

    def __init__(self, seller_id=None, name=None, category=None,
                 description=None, price=None, stock=0, image=None):
        self.seller_id   = seller_id
        self.name        = name
        self.category    = category
        self.description = description
        self.stock       = stock
        self.image       = image
        self.__price     = None
        if price is not None:
            self.set_price(price)

    # ── Encapsulation: Price ─────────────────────────────────────

    def set_price(self, price):
        price = float(price)
        if price < 0:
            raise ValueError("Price cannot be negative.")
        self.__price = price

    def get_price(self):
        return self.__price

    # ── Save ─────────────────────────────────────────────────────

    def save(self):
        db = Database()
        pid = db.execute_returning_id(
            """INSERT INTO products (seller_id, name, category, description, price, stock, image)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (self.seller_id, self.name, self.category, self.description,
             self.__price, self.stock, self.image),
        )
        db.close()
        return pid

    def update(self, product_id):
        db = Database()
        db.execute(
            """UPDATE products SET name=%s, category=%s, description=%s,
               price=%s, stock=%s, image=%s WHERE product_id=%s""",
            (self.name, self.category, self.description,
             self.__price, self.stock, self.image, product_id),
        )
        db.close()

    def soft_delete(self, product_id):
        db = Database()
        db.execute("UPDATE products SET is_active=0 WHERE product_id=%s", (product_id,))
        db.close()

    # ── Queries ──────────────────────────────────────────────────

    @staticmethod
    def get_all_active(limit=None):
        """Return all active products with seller business name."""
        db = Database()
        sql = """
            SELECT p.*, s.business_name AS seller_business_name,
                   s.whatsapp_number, s.seller_id AS sid
            FROM products p
            JOIN sellers s ON p.seller_id = s.seller_id
            WHERE p.is_active = 1
            ORDER BY p.created_at DESC
        """
        if limit:
            sql += f" LIMIT {int(limit)}"
        results = db.fetch_all(sql)
        db.close()
        return results

    @staticmethod
    def get_by_id(product_id):
        db = Database()
        result = db.fetch_one(
            """SELECT p.*, s.business_name AS seller_business_name,
                      s.whatsapp_number, s.business_phone, s.business_address,
                      s.seller_id AS sid, u.full_name AS seller_full_name,
                      u.email AS seller_email
               FROM products p
               JOIN sellers s ON p.seller_id = s.seller_id
               JOIN users   u ON s.user_id    = u.id
               WHERE p.product_id=%s AND p.is_active=1""",
            (product_id,)
        )
        db.close()
        return result

    @staticmethod
    def get_by_seller(seller_id):
        db = Database()
        results = db.fetch_all(
            "SELECT * FROM products WHERE seller_id=%s ORDER BY created_at DESC",
            (seller_id,)
        )
        db.close()
        return results

    @staticmethod
    def search(query, category=None):
        db = Database()
        like = f"%{query}%"
        if category:
            results = db.fetch_all(
                """SELECT p.*, s.business_name AS seller_business_name, s.whatsapp_number
                   FROM products p JOIN sellers s ON p.seller_id=s.seller_id
                   WHERE p.is_active=1 AND p.category=%s
                     AND (p.name LIKE %s OR p.description LIKE %s OR s.business_name LIKE %s)
                   ORDER BY p.created_at DESC""",
                (category, like, like, like)
            )
        else:
            results = db.fetch_all(
                """SELECT p.*, s.business_name AS seller_business_name, s.whatsapp_number
                   FROM products p JOIN sellers s ON p.seller_id=s.seller_id
                   WHERE p.is_active=1
                     AND (p.name LIKE %s OR p.description LIKE %s OR s.business_name LIKE %s)
                   ORDER BY p.created_at DESC""",
                (like, like, like)
            )
        db.close()
        return results

    @staticmethod
    def get_by_category(category):
        db = Database()
        results = db.fetch_all(
            """SELECT p.*, s.business_name AS seller_business_name, s.whatsapp_number
               FROM products p JOIN sellers s ON p.seller_id=s.seller_id
               WHERE p.is_active=1 AND p.category=%s
               ORDER BY p.created_at DESC""",
            (category,)
        )
        db.close()
        return results

    @staticmethod
    def get_trending(limit=6):
        """Most viewed products via view_history join."""
        db = Database()
        results = db.fetch_all(
            """SELECT p.*, s.business_name AS seller_business_name, s.whatsapp_number,
                      COUNT(vh.history_id) AS view_count
               FROM products p
               JOIN sellers s ON p.seller_id=s.seller_id
               LEFT JOIN view_history vh ON p.product_id=vh.product_id
               WHERE p.is_active=1
               GROUP BY p.product_id
               ORDER BY view_count DESC, p.created_at DESC
               LIMIT %s""",
            (limit,)
        )
        db.close()
        return results

    @staticmethod
    def get_categories():
        db = Database()
        results = db.fetch_all(
            "SELECT DISTINCT category FROM products WHERE is_active=1 ORDER BY category"
        )
        db.close()
        return [r["category"] for r in results]

    @staticmethod
    def get_analytics_for_seller(seller_id):
        """Return per-product view count + order count for seller dashboard."""
        db = Database()
        results = db.fetch_all(
            """SELECT p.product_id, p.name, p.price, p.stock,
                      COUNT(DISTINCT vh.history_id) AS view_count,
                      COUNT(DISTINCT o.order_id)   AS order_count,
                      COALESCE(SUM(o.total_amount), 0) AS revenue
               FROM products p
               LEFT JOIN view_history vh ON p.product_id=vh.product_id
               LEFT JOIN orders o ON p.product_id=o.product_id
                         AND o.order_status != 'cancelled'
               WHERE p.seller_id=%s AND p.is_active=1
               GROUP BY p.product_id
               ORDER BY revenue DESC""",
            (seller_id,)
        )
        db.close()
        return results

    # ── Factory ──────────────────────────────────────────────────

    @classmethod
    def from_db(cls, data):
        if data is None:
            return None
        p = cls(
            seller_id=data.get("seller_id"),
            name=data.get("name"),
            category=data.get("category"),
            description=data.get("description"),
            price=data.get("price"),
            stock=data.get("stock", 0),
            image=data.get("image"),
        )
        return p

    def __str__(self):
        return f"Product(name={self.name}, price={self.__price})"

    def __repr__(self):
        return f"<Product name={self.name}>"

    def __eq__(self, other):
        return isinstance(other, Product) and self.name == other.name