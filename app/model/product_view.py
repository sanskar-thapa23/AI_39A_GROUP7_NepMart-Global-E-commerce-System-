from app.model.basemodel import BaseModel
from .database import Database


class ProductView(BaseModel):
    """
    ProductView Model — tracks product view events for analytics and recommendations.
    """

    @property
    def table(self):
        return "product_views"

    def __init__(self, user_id=None, product_id=None, viewed_at=None, id=None):
        self.id = id
        self.user_id = user_id
        self.product_id = product_id
        self.viewed_at = viewed_at

    def save(self):
        """Save the product view event to the database."""
        db = Database()
        db.execute(
            "INSERT INTO product_views (user_id, product_id) VALUES (%s, %s)",
            (self.user_id, self.product_id)
        )
        db.close()
