from datetime import datetime, timedelta
from flask import flash
from app.model.database import Database
from app.controller.basecontroller import BaseController


class CouponController(BaseController):
    def __init__(self):
        self.db = Database()

    def cleanup_expired_coupons(self):
        try:
            self.db.execute("DELETE FROM coupons WHERE expires_at < NOW()")
        except Exception:
            pass

    def get_vendor_coupons(self, vendor_id):
        self.cleanup_expired_coupons()
        try:
            return self.db.fetch_all(
                "SELECT * FROM coupons WHERE vendor_id = %s ORDER BY created_at DESC",
                (vendor_id,),
            )
        except Exception:
            return []

    def get_coupon(self, coupon_id, vendor_id=None):
        self.cleanup_expired_coupons()
        try:
            if vendor_id:
                return self.db.fetch_one(
                    "SELECT * FROM coupons WHERE id = %s AND vendor_id = %s",
                    (coupon_id, vendor_id),
                )
            return self.db.fetch_one("SELECT * FROM coupons WHERE id = %s", (coupon_id,))
        except Exception:
            return None

    def get_coupon_by_code(self, coupon_code):
        self.cleanup_expired_coupons()
        return self.db.fetch_one(
            "SELECT * FROM coupons WHERE coupon_code = %s",
            (coupon_code.strip().upper(),),
        )

    def create_coupon(self, vendor_id, coupon_code, discount_percentage, duration_days):
        coupon_code = coupon_code.strip().upper()
        discount_percentage = int(discount_percentage)
        duration_days = int(duration_days)

        if not coupon_code or discount_percentage <= 0 or discount_percentage > 100 or duration_days <= 0:
            flash("Please provide a valid coupon code, discount percent, and duration.", "danger")
            return False

        existing = self.db.fetch_one(
            "SELECT id FROM coupons WHERE coupon_code = %s",
            (coupon_code,),
        )
        if existing:
            flash("Coupon code already exists. Please choose a different code.", "danger")
            return False

        expires_at = datetime.now() + timedelta(days=duration_days)
        self.db.execute(
            "INSERT INTO coupons (coupon_code, discount_percentage, vendor_id, expires_at, created_by) VALUES (%s, %s, %s, %s, %s)",
            (coupon_code, discount_percentage, vendor_id, expires_at, vendor_id),
        )
        flash(f"Coupon '{coupon_code}' created successfully.", "success")
        return True

    def update_coupon(self, coupon_id, vendor_id, coupon_code, discount_percentage, duration_days):
        coupon_code = coupon_code.strip().upper()
        discount_percentage = int(discount_percentage)
        duration_days = int(duration_days)

        if not coupon_code or discount_percentage <= 0 or discount_percentage > 100 or duration_days <= 0:
            flash("Please provide a valid coupon code, discount percent, and duration.", "danger")
            return False

        existing = self.db.fetch_one(
            "SELECT id FROM coupons WHERE coupon_code = %s AND id != %s",
            (coupon_code, coupon_id),
        )
        if existing:
            flash("Another coupon already uses that code. Choose a different code.", "danger")
            return False

        expires_at = datetime.now() + timedelta(days=duration_days)
        self.db.execute(
            "UPDATE coupons SET coupon_code = %s, discount_percentage = %s, expires_at = %s WHERE id = %s AND vendor_id = %s",
            (coupon_code, discount_percentage, expires_at, coupon_id, vendor_id),
        )
        flash(f"Coupon '{coupon_code}' updated successfully.", "success")
        return True

    def delete_coupon(self, coupon_id, vendor_id):
        self.db.execute(
            "DELETE FROM coupons WHERE id = %s AND vendor_id = %s",
            (coupon_id, vendor_id),
        )
        flash("Coupon deleted successfully.", "success")
        return True

    def close(self):
        self.db.close()
