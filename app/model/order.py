"""
=============================================================
  NepMart — Order Model
=============================================================
"""

from app.model.basemodel import BaseModel
from .database import Database


class Order(BaseModel):

    @property
    def table(self):
        return "orders"

    VALID_STATUSES = ("pending", "confirmed", "shipped", "delivered", "cancelled")

    def __init__(self, buyer_id=None, product_id=None,
                 quantity=1, total_amount=0.0, order_status="pending"):
        self.buyer_id     = buyer_id
        self.product_id   = product_id
        self.quantity     = quantity
        self.total_amount = total_amount
        self.order_status = order_status if order_status in self.VALID_STATUSES else "pending"

    # ── Save ─────────────────────────────────────────────────────

    def save(self):
        db = Database()
        oid = db.execute_returning_id(
            """INSERT INTO orders (buyer_id, product_id, quantity, total_amount, order_status)
               VALUES (%s, %s, %s, %s, %s)""",
            (self.buyer_id, self.product_id, self.quantity,
             self.total_amount, self.order_status),
        )
        db.close()
        return oid

    @staticmethod
    def update_status(order_id, status):
        db = Database()
        db.execute(
            "UPDATE orders SET order_status=%s WHERE order_id=%s",
            (status, order_id)
        )
        db.close()

    # ── Lookups ──────────────────────────────────────────────────

    @staticmethod
    def get_by_buyer(buyer_id):
        db = Database()
        results = db.fetch_all(
            """SELECT o.*, p.name AS product_name, p.image AS product_image,
                      p.category AS product_category,
                      s.business_name AS seller_name
               FROM orders o
               JOIN products p ON o.product_id=p.product_id
               JOIN sellers  s ON p.seller_id=s.seller_id
               WHERE o.buyer_id=%s
               ORDER BY o.created_at DESC""",
            (buyer_id,)
        )
        db.close()
        return results

    @staticmethod
    def get_by_seller(seller_id):
        db = Database()
        results = db.fetch_all(
            """SELECT o.*, p.name AS product_name, p.image AS product_image,
                      u.full_name AS buyer_name, u.email AS buyer_email,
                      u.phone AS buyer_phone
               FROM orders o
               JOIN products p ON o.product_id=p.product_id
               JOIN users    u ON o.buyer_id=u.id
               WHERE p.seller_id=%s
               ORDER BY o.created_at DESC""",
            (seller_id,)
        )
        db.close()
        return results

    @staticmethod
    def get_by_id(order_id):
        db = Database()
        result = db.fetch_one(
            """SELECT o.*, p.name AS product_name, s.business_name AS seller_name,
                      u.full_name AS buyer_name
               FROM orders o
               JOIN products p ON o.product_id=p.product_id
               JOIN sellers  s ON p.seller_id=s.seller_id
               JOIN users    u ON o.buyer_id=u.id
               WHERE o.order_id=%s""",
            (order_id,)
        )
        db.close()
        return result
