from werkzeug.security import generate_password_hash, check_password_hash
from app.model.basemodel import BaseModel
from .database import Database


class User(BaseModel):

    # ── Polymorphism ──
    @property
    def table(self):
        return "users"

    # ── Constructor (FIXED: username instead of name) ──
    def __init__(self, username=None, email=None, password=None, role="customer"):
        self.username = username
        self.email = email
        self.__password = None
        self.role = role

        if password:
            self.set_password(password)

    # ── Password Encapsulation ──
    def set_password(self, plain_password):
        self.__password = generate_password_hash(plain_password)

    def check_password(self, plain_password):
        if self.__password is None:
            return False
        return check_password_hash(self.__password, plain_password)

    # ── Save user ──
    def save(self):
        db = Database()
        db.execute(
            "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
            (self.username, self.email, self.__password, self.role),
        )
        db.close()

    # ── Update user ──
    def update(self, user_id, update_password=False):
        db = Database()

        if update_password:
            db.execute(
                "UPDATE users SET username=%s, email=%s, password=%s, role=%s WHERE id=%s",
                (self.username, self.email, self.__password, self.role, user_id),
            )
        else:
            db.execute(
                "UPDATE users SET username=%s, email=%s, role=%s WHERE id=%s",
                (self.username, self.email, self.role, user_id),
            )

        db.close()

    # ── Profile update ──
    def update_profile(self, user_id, update_password=False):
        db = Database()

        if update_password:
            db.execute(
                "UPDATE users SET username=%s, email=%s, password=%s WHERE id=%s",
                (self.username, self.email, self.__password, user_id),
            )
        else:
            db.execute(
                "UPDATE users SET username=%s, email=%s WHERE id=%s",
                (self.username, self.email, user_id),
            )

        db.close()

    # ── Email check ──
    def email_exists(self, exclude_id=None):
        db = Database()

        if exclude_id:
            result = db.fetch_one(
                "SELECT id FROM users WHERE email = %s AND id != %s",
                (self.email, exclude_id),
            )
        else:
            result = db.fetch_one(
                "SELECT id FROM users WHERE email = %s",
                (self.email,),
            )

        db.close()
        return result is not None

    # ── Username check ──
    def username_exists(self, exclude_id=None):
        db = Database()

        if exclude_id:
            result = db.fetch_one(
                "SELECT id FROM users WHERE username = %s AND id != %s",
                (self.username, exclude_id),
            )
        else:
            result = db.fetch_one(
                "SELECT id FROM users WHERE username = %s",
                (self.username,),
            )

        db.close()
        return result is not None

    # ── From DB ──
    @classmethod
    def from_db(cls, data):
        if data is None:
            return None

        user = cls()
        user.username = data["username"]
        user.email = data["email"]
        user.__password = data["password"]
        user.role = data["role"]

        return user

    # ── Delete user account ──
    def delete_account(self, user_id):
        """Delete a user account by ID."""
        db = Database()
        db.execute("DELETE FROM users WHERE id=%s", (user_id,))
        db.close()

    # ── Debug ──
    def __str__(self):
        return f"User(username={self.username}, email={self.email}, role={self.role})"

    def __repr__(self):
        return f"<User email={self.email}>"