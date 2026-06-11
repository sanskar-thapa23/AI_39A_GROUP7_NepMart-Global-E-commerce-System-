from werkzeug.security import generate_password_hash, check_password_hash
from app.model.basemodel import BaseModel
from .database import Database


class Vendor(BaseModel):

    # ── Polymorphism ──
    @property
    def table(self):
        return "vendors"

    # ── Constructor (Tailored for Vendor Data, No Profile Pictures) ──
    def __init__(self, business_name=None, email=None, password=None, is_verified=True):
        self.business_name = business_name
        self.email = email
        self.__password = None
        self.is_verified = is_verified  # Boolean: matches front-end tracking badge

        if password:
            self.set_password(password)

    # ── Password Encapsulation ──
    def set_password(self, plain_password):
        self.__password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        if self.__password is None:
            return False
        return check_password_hash(self.__password, plain_password)

    # ── Save Vendor ──
    def save(self):
        db = Database()
        db.execute(
            "INSERT INTO vendors (business_name, email, password, is_verified) VALUES (%s, %s, %s, %s)",
            (self.business_name, self.email, self.__password, self.is_verified),
        )
        db.close()

    # ── Update Vendor (Full Administrative Update) ──
    def update(self, vendor_id, update_password=False):
        db = Database()

        if update_password:
            db.execute(
                "UPDATE vendors SET business_name=%s, email=%s, password=%s, is_verified=%s WHERE id=%s",
                (self.business_name, self.email, self.__password, self.is_verified, vendor_id),
            )
        else:
            db.execute(
                "UPDATE vendors SET business_name=%s, email=%s, is_verified=%s WHERE id=%s",
                (self.business_name, self.email, self.is_verified, vendor_id),
            )

        db.close()

    # ── Profile Update (Self-service profile modifications) ──
    def update_profile(self, vendor_id, update_password=False):
        db = Database()

        if update_password:
            db.execute(
                "UPDATE vendors SET business_name=%s, email=%s, password=%s WHERE id=%s",
                (self.business_name, self.email, self.__password, vendor_id),
            )
        else:
            db.execute(
                "UPDATE vendors SET business_name=%s, email=%s WHERE id=%s",
                (self.business_name, self.email, vendor_id),
            )

        db.close()

    # ── Email Unique Validation Check ──
    def email_exists(self, exclude_id=None):
        db = Database()

        if exclude_id:
            result = db.fetch_one(
                "SELECT id FROM vendors WHERE email = %s AND id != %s",
                (self.email, exclude_id),
            )
        else:
            result = db.fetch_one(
                "SELECT id FROM vendors WHERE email = %s",
                (self.email,),
            )

        db.close()
        return result is not None

    # ── Business Name Unique Validation Check ──
    def business_name_exists(self, exclude_id=None):
        db = Database()

        if exclude_id:
            result = db.fetch_one(
                "SELECT id FROM vendors WHERE business_name = %s AND id != %s",
                (self.business_name, exclude_id),
            )
        else:
            result = db.fetch_one(
                "SELECT id FROM vendors WHERE business_name = %s",
                (self.business_name,),
            )

        db.close()
        return result is not None

    # ── Hydrate Object Factory From DB Result Array/Dict ──
    @classmethod
    def from_db(cls, data):
        if data is None:
            return None

        vendor = cls()
        vendor.business_name = data["business_name"]
        vendor.email = data["email"]
        vendor.__password = data["password"]
        vendor.is_verified = bool(data["is_verified"])

        return vendor

    # ── Debug representations ──
    def __str__(self):
        return f"Vendor(business_name={self.business_name}, email={self.email}, is_verified={self.is_verified})"

    def __repr__(self):
        return f"<Vendor email={self.email}>"