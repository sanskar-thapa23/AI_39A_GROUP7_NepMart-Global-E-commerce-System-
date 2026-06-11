"""
=============================================================
  NepMart — User Model
=============================================================
  Inherits BaseModel. Handles buyer/seller/admin accounts.
  Encapsulates password hashing.
=============================================================
"""

from werkzeug.security import generate_password_hash, check_password_hash
from app.model.basemodel import BaseModel
from .database import Database


class User(BaseModel):

    @property
    def table(self):
        return "users"

    def __init__(self, full_name=None, email=None, password=None,
                 role="buyer", phone=None):
        self.full_name = full_name
        self.email     = email
        self.role      = role
        self.phone     = phone
        self.__password_hash = None
        if password:
            self.set_password(password)

    # ── Encapsulation: Password ──────────────────────────────────

    def set_password(self, plain):
        self.__password_hash = generate_password_hash(plain)

    def check_password(self, plain):
        if not self.__password_hash:
            return False
        return check_password_hash(self.__password_hash, plain)

    def get_password_hash(self):
        return self.__password_hash

    # ── Save / Update ────────────────────────────────────────────

    def save(self):
        """Insert a new user and return the new ID."""
        db = Database()
        uid = db.execute_returning_id(
            "INSERT INTO users (full_name, email, password_hash, role, phone) "
            "VALUES (%s, %s, %s, %s, %s)",
            (self.full_name, self.email, self.__password_hash, self.role, self.phone),
        )
        db.close()
        return uid

    def update_profile(self, user_id, update_password=False):
        db = Database()
        if update_password:
            db.execute(
                "UPDATE users SET full_name=%s, email=%s, phone=%s, password_hash=%s WHERE id=%s",
                (self.full_name, self.email, self.phone, self.__password_hash, user_id),
            )
        else:
            db.execute(
                "UPDATE users SET full_name=%s, email=%s, phone=%s WHERE id=%s",
                (self.full_name, self.email, self.phone, user_id),
            )
        db.close()

    # ── Lookups ──────────────────────────────────────────────────

    def find_by_email(self, email):
        db = Database()
        result = db.fetch_one("SELECT * FROM users WHERE email = %s", (email,))
        db.close()
        return result

    def email_exists(self, exclude_id=None):
        db = Database()
        if exclude_id:
            result = db.fetch_one(
                "SELECT id FROM users WHERE email=%s AND id!=%s", (self.email, exclude_id)
            )
        else:
            result = db.fetch_one("SELECT id FROM users WHERE email=%s", (self.email,))
        db.close()
        return result is not None

    # ── Factory ──────────────────────────────────────────────────

    @classmethod
    def from_db(cls, data):
        if data is None:
            return None
        u = cls()
        u.full_name = data.get("full_name")
        u.email     = data.get("email")
        u.role      = data.get("role", "buyer")
        u.phone     = data.get("phone")
        u.__password_hash = data.get("password_hash")
        # Patch name-mangled attr for check_password to work
        u._User__password_hash = data.get("password_hash")
        return u

    def __str__(self):
        return f"User(name={self.full_name}, email={self.email}, role={self.role})"

    def __repr__(self):
        return f"<User email={self.email}>"