"""
=============================================================
OOP Concept: INHERITANCE, ENCAPSULATION & POLYMORPHISM
=============================================================
- Inheritance: Product inherits from BaseModel.
- Encapsulation: Price is kept private (__product_price) with validation.
- Polymorphism: Product overrides the abstract 'table' property.
=============================================================
"""

from decimal import Decimal
from app.model.basemodel import BaseModel
from .database import Database


class Product(BaseModel):

    """
    Product Model — simplified for e-commerce system.

    Fields:
        - product_image       : URL/path of product image
        - product_name        : Name of product
        - product_prices      : List of price variants
        - category            : Product category
        - location            : Product origin location
        - product_price       : Main product price (encapsulated)
        - product_description : Product description
        - rating              : Average rating
        - reviews_count       : Total review count
    """

    # ---------------- POLYMORPHISM ----------------
    @property
    def table(self):
        """Return database table name."""
        return "products"

    # ---------------- CONSTRUCTOR ----------------
    def __init__(
        self,
        product_image=None,
        product_name=None,
        product_prices=None,
        product_price=None,
        category=None,
        location=None,
        product_description=None,
        rating=0,
        reviews_count=0,
        id=None,
        vendor_name=None,
    ):
        self.id = id
        self.vendor_name = vendor_name
        self.product_image = product_image
        self.product_name = product_name
        self.product_prices = product_prices or []
        self.category = category
        self.location = location
        self.__product_price = None
        self.product_description = product_description
        self.rating = rating
        self.reviews_count = reviews_count

        # validate price during initialization
        if product_price is not None:
            self.set_product_price(product_price)

    # ---------------- ENCAPSULATION ----------------
    @property
    def product_price(self):
        return self.__product_price

    def get_product_price(self):
        return self.__product_price

    def set_product_price(self, price):

        if price is None:
            raise ValueError("Product price is required.")

        if not isinstance(price, (int, float, Decimal)):
            raise TypeError("Product price must be a number.")

        if price < 0:
            raise ValueError("Product price cannot be negative.")

        self.__product_price = float(price)

    # ---------------- CREATE ----------------
    def save(self, user_id):

        db = Database()

        db.execute(
            """
            INSERT INTO products
            (product_image, product_name, product_prices, product_price, category, location, product_description)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                self.product_image,
                self.product_name,
                str(self.product_prices),
                self.__product_price,
                self.category,
                self.location,
                self.product_description,
            ),
        )

        # Get the ID of the product just inserted
        last_id_data = db.fetch_one("SELECT LAST_INSERT_ID() AS id")
        product_id = last_id_data['id']

        # Map product to the vendor/user in the pivot table
        db.execute(
            "INSERT INTO user_products (user_id, product_id) VALUES (%s, %s)",
            (user_id, product_id)
        )

        db.close()

    # ---------------- UPDATE ----------------
    def update(self, product_id):

        db = Database()

        db.execute(
            """
            UPDATE products
            SET product_image=%s,
                product_name=%s,
                product_prices=%s,
                product_price=%s,
                category=%s,
                location=%s,
                product_description=%s
            WHERE id=%s
            """,
            (
                self.product_image,
                self.product_name,
                str(self.product_prices),
                self.__product_price,
                self.category,
                self.location,
                self.product_description,
                product_id,
            ),
        )

        db.close()

    # ---------------- FROM DATABASE ----------------
    @classmethod
    def from_db(cls, data):

        if not data:
            return None

        return cls(
            product_image=data.get("product_image"),
            product_name=data.get("product_name"),
            product_prices=data.get("product_prices"),
            product_price=data.get("product_price"),
            category=data.get("category"),
            location=data.get("location"),
            rating=data.get("rating", 0),
            reviews_count=data.get("reviews_count", 0),
            product_description=data.get("product_description"),
            id=data.get("id"),
            vendor_name=data.get("vendor_name"),
        )

    # ---------------- MAGIC METHODS ----------------
    def __str__(self):
        return f"Product(name={self.product_name}, price={self.__product_price})"

    def __repr__(self):
        return f"<Product {self.product_name}>"

    def __eq__(self, other):
        if isinstance(other, Product):
            return self.product_name == other.product_name
        return False