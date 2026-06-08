# app/controller/productcontroller.py

from app.model.product import Product


class ProductController:
    """
    Controller layer for product-related business logic.
    Sits between the routes (HTTP) and the model (DB).
    """

    def __init__(self):
        self.product_model = Product()

    def list_all(self):
        """Return every product in the catalog."""
        return self.product_model.find_all()

    def get(self, product_id):
        """Return one product by ID, or None."""
        return self.product_model.find_by_id(product_id)

    def total_count(self):
        """How many products exist."""
        return self.product_model.count_all()

    def search(self, keyword):
        """Naive case-insensitive name search."""
        all_products = self.product_model.find_all()
        keyword = keyword.lower().strip()
        return [
            p for p in all_products
            if keyword in p["name"].lower()
            or keyword in (p.get("description") or "").lower()
        ]