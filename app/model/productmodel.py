"""
=============================================================
OOP Concept: INHERITANCE, ENCAPSULATION & POLYMORPHISM
=============================================================
- Inheritance: Product inherits from BaseModel.
- Encapsulation: Price is kept private (__product_price) with validation.
- Polymorphism: Product overrides the abstract 'table' property.
=============================================================
"""

from app.model.basemodel import BaseModel
from .database import Database


class Product(BaseModel):

    """
    Product Model — simplified for e-commerce system.

    Fields:
        - product_image       : URL/path of product image
        - product_name        : Name of product
        - product_prices      : List of price variants
        - product_price       : Main product price (encapsulated)
        - product_description : Product description
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
        product_description=None,
    ):
        self.product_image = product_image
        self.product_name = product_name
        self.product_prices = product_prices or []
        self.__product_price = None
        self.product_description = product_description

        # validate price during initialization
        if product_price is not None:
            self.set_product_price(product_price)

    # ---------------- ENCAPSULATION ----------------
    def get_product_price(self):
        return self.__product_price

    def set_product_price(self, price):

        if price is None:
            raise ValueError("Product price is required.")

        if not isinstance(price, (int, float)):
            raise TypeError("Product price must be a number.")

        if price < 0:
            raise ValueError("Product price cannot be negative.")

        self.__product_price = float(price)

    # ---------------- CREATE ----------------
    def save(self):

        db = Database()

        db.execute(
            """
            INSERT INTO products
            (product_image, product_name, product_prices, product_price, product_description)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                self.product_image,
                self.product_name,
                str(self.product_prices),
                self.__product_price,
                self.product_description,
            ),
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
                product_description=%s
            WHERE id=%s
            """,
            (
                self.product_image,
                self.product_name,
                str(self.product_prices),
                self.__product_price,
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
            product_description=data.get("product_description"),
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