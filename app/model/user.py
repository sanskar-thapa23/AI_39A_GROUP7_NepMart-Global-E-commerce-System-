from app.model.database import Database


class User:

    def __init__(self):
        self.db = Database()
        self.cursor = self.db.cursor

    def get_user_by_username(self, username):
        query = "SELECT * FROM users WHERE username=%s"
        self.cursor.execute(query, (username,))
        return self.cursor.fetchone()