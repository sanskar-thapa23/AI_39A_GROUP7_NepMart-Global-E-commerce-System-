"""
=============================================================
  NepMart — Seller Model
=============================================================
  Full seller business profile with company details,
  WhatsApp, logo, and dashboard stats.
=============================================================
"""

from app.model.basemodel import BaseModel
from .database import Database


class Seller(BaseModel):

    @property
    def table(self):
        return "sellers"

    def __init__(self, user_id=None, company_name=None, company_type=None,
                 whatsapp_number=None, business_phone=None,
                 company_description=None, business_address=None,
                 company_logo=None, business_registration_number=None):
        self.user_id                      = user_id
        self.company_name                 = company_name
        self.company_type                 = company_type
        self.whatsapp_number              = whatsapp_number
        self.business_phone               = business_phone
        self.company_description          = company_description
        self.business_address             = business_address
        self.company_logo                 = company_logo
        self.business_registration_number = business_registration_number

    # ── Save / Update ────────────────────────────────────────────

    def save(self):
        db = Database()
        sid = db.execute_returning_id(
            """INSERT INTO sellers
               (user_id, company_name, company_type, whatsapp_number, business_phone,
                company_description, business_address, company_logo, business_registration_number)
               VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
            (self.user_id, self.company_name, self.company_type,
             self.whatsapp_number, self.business_phone,
             self.company_description, self.business_address,
             self.company_logo, self.business_registration_number),
        )
        db.close()
        return sid

    def update(self, seller_id):
        db = Database()
        db.execute(
            """UPDATE sellers SET company_name=%s, company_type=%s, whatsapp_number=%s,
               business_phone=%s, company_description=%s, business_address=%s
               WHERE seller_id=%s""",
            (self.company_name, self.company_type, self.whatsapp_number,
             self.business_phone, self.company_description,
             self.business_address, seller_id),
        )
        db.close()

    def update_logo(self, seller_id, logo_path):
        db = Database()
        db.execute(
            "UPDATE sellers SET company_logo=%s WHERE seller_id=%s",
            (logo_path, seller_id)
        )
        db.close()

    # ── Lookups ──────────────────────────────────────────────────

    @staticmethod
    def find_by_user_id(user_id):
        db = Database()
        result = db.fetch_one(
            "SELECT * FROM sellers WHERE user_id=%s", (user_id,)
        )
        db.close()
        return result

    @staticmethod
    def get_all_with_user():
        """Join sellers + users for the Sellers Directory."""
        db = Database()
        results = db.fetch_all(
            """SELECT s.*, u.full_name, u.email, u.phone_number,
                      COUNT(DISTINCT p.product_id) AS product_count
               FROM sellers s
               JOIN users u ON s.user_id = u.id
               LEFT JOIN products p ON s.seller_id = p.seller_id AND p.is_active=1
               GROUP BY s.seller_id
               ORDER BY s.created_at DESC"""
        )
        db.close()
        return results

    @staticmethod
    def get_with_user(seller_id):
        db = Database()
        result = db.fetch_one(
            """SELECT s.*, u.full_name, u.email, u.phone_number,
                      COUNT(DISTINCT p.product_id) AS product_count
               FROM sellers s
               JOIN users u ON s.user_id = u.id
               LEFT JOIN products p ON s.seller_id = p.seller_id AND p.is_active=1
               WHERE s.seller_id=%s
               GROUP BY s.seller_id""",
            (seller_id,)
        )
        db.close()
        return result

    @staticmethod
    def get_dashboard_stats(seller_id):
        db = Database()
        stats = {}

        row = db.fetch_one(
            "SELECT COUNT(*) AS cnt FROM products WHERE seller_id=%s AND is_active=1",
            (seller_id,)
        )
        stats["total_products"] = row["cnt"] if row else 0

        row = db.fetch_one(
            """SELECT COUNT(*) AS cnt FROM orders o
               JOIN products p ON o.product_id=p.product_id
               WHERE p.seller_id=%s AND o.order_status!='cancelled'""",
            (seller_id,)
        )
        stats["total_orders"] = row["cnt"] if row else 0

        row = db.fetch_one(
            """SELECT COALESCE(SUM(o.total_amount),0) AS rev FROM orders o
               JOIN products p ON o.product_id=p.product_id
               WHERE p.seller_id=%s AND o.order_status NOT IN ('cancelled','pending')""",
            (seller_id,)
        )
        stats["total_revenue"] = float(row["rev"]) if row else 0.0

        row = db.fetch_one(
            """SELECT COUNT(*) AS cnt FROM view_history vh
               JOIN products p ON vh.product_id=p.product_id
               WHERE p.seller_id=%s""",
            (seller_id,)
        )
        stats["total_views"] = row["cnt"] if row else 0

        row = db.fetch_one(
            """SELECT COUNT(DISTINCT o.buyer_id) AS cnt FROM orders o
               JOIN products p ON o.product_id=p.product_id
               WHERE p.seller_id=%s""",
            (seller_id,)
        )
        stats["total_buyers"] = row["cnt"] if row else 0

        row = db.fetch_one(
            """SELECT COUNT(*) AS cnt FROM recommendations r
               JOIN products p ON r.product_id=p.product_id
               WHERE p.seller_id=%s""",
            (seller_id,)
        )
        stats["total_recommendations"] = row["cnt"] if row else 0

        db.close()
        return stats

    # ── Factory ──────────────────────────────────────────────────

    @classmethod
    def from_db(cls, data):
        if data is None:
            return None
        return cls(
            user_id=data.get("user_id"),
            company_name=data.get("company_name"),
            company_type=data.get("company_type"),
            whatsapp_number=data.get("whatsapp_number"),
            business_phone=data.get("business_phone"),
            company_description=data.get("company_description"),
            business_address=data.get("business_address"),
            company_logo=data.get("company_logo"),
            business_registration_number=data.get("business_registration_number"),
        )

    def __str__(self):
        return f"Seller(company={self.company_name})"
