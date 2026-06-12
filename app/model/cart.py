"""
=============================================================
  NepMart — Cart Model
=============================================================
  DB-backed cart for logged-in buyers.
  Session-based fallback handled in buyer_controller.
=============================================================
"""

from .database import Database


class Cart:

    @staticmethod
    def add(user_id, product_id, quantity=1):
        """Add item or increment quantity if already in cart."""
        db = Database()
        existing = db.fetch_one(
            "SELECT cart_id, quantity FROM cart WHERE user_id=%s AND product_id=%s",
            (user_id, product_id)
        )
        if existing:
            db.execute(
                "UPDATE cart SET quantity=quantity+%s WHERE cart_id=%s",
                (quantity, existing["cart_id"])
            )
        else:
            db.execute(
                "INSERT INTO cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                (user_id, product_id, quantity)
            )
        db.close()

    @staticmethod
    def remove(user_id, product_id):
        db = Database()
        db.execute(
            "DELETE FROM cart WHERE user_id=%s AND product_id=%s",
            (user_id, product_id)
        )
        db.close()

    @staticmethod
    def clear(user_id):
        db = Database()
        db.execute("DELETE FROM cart WHERE user_id=%s", (user_id,))
        db.close()

    @staticmethod
    def get_items(user_id):
        """Return cart rows with full product info."""
        db = Database()
        results = db.fetch_all(
            """SELECT c.cart_id, c.quantity, p.product_id, p.seller_id, p.name, p.price,
                      p.image_path, p.stock, p.category,
                      s.company_name AS seller_name, s.whatsapp_number,
                      (p.price * c.quantity) AS subtotal
               FROM cart c
               JOIN products p ON c.product_id=p.product_id
               JOIN sellers  s ON p.seller_id=s.seller_id
               WHERE c.user_id=%s AND p.is_active=1
               ORDER BY c.added_at DESC""",
            (user_id,)
        )
        db.close()
        return results

    @staticmethod
    def get_total(user_id):
        db = Database()
        row = db.fetch_one(
            """SELECT COALESCE(SUM(p.price * c.quantity), 0) AS total
               FROM cart c JOIN products p ON c.product_id=p.product_id
               WHERE c.user_id=%s AND p.is_active=1""",
            (user_id,)
        )
        db.close()
        return float(row["total"]) if row else 0.0

    @staticmethod
    def count(user_id):
        db = Database()
        row = db.fetch_one(
            "SELECT COALESCE(SUM(quantity),0) AS cnt FROM cart WHERE user_id=%s",
            (user_id,)
        )
        db.close()
        return int(row["cnt"]) if row else 0

    @staticmethod
    def update_quantity(cart_id, quantity):
        db = Database()
        if quantity <= 0:
            db.execute("DELETE FROM cart WHERE cart_id=%s", (cart_id,))
        else:
            db.execute("UPDATE cart SET quantity=%s WHERE cart_id=%s", (quantity, cart_id))
        db.close()
