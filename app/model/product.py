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
    Product Model — simplified for standard e-commerce display.
    
    Fields:
      - product_image      : URL/path to product image
      - product_name       : Display name
      - product_prices     : List of price options/variants
      - product_price      : Main required price (encapsulated)
      - product_description: Product details
    """

    @property
    def table(self):
        """Polymorphism: Tell BaseModel which database table to use."""
        return "products"

    def __init__(
        self,
        product_image=None,
        product_name=None,
        product_prices=None,
        product_price=None,
        product_description=None,
    ):
        """
        Create a Product object.
        
        Encapsulation:
          - __product_price is PRIVATE (double underscore).
          - It can only be set through the setter to enforce validation.
        """
        self.product_image = product_image
        self.product_name = product_name
        self.product_prices = product_prices or []
        self.__product_price = None
        self.product_description = product_description

        # Validate required price on init
        if product_price is not None:
            self.set_product_price(product_price)

    # ── Encapsulation: Price Management ─────────────────────

    def get_product_price(self):
        """Get the main product price."""
        return self.__product_price

    def set_product_price(self, price):
        """
        Set product price with validation.
        * Required field — must be a positive number.
        """
        if price is None:
            raise ValueError("Product price is required.")
        if not isinstance(price, (int, float)):
            raise TypeError("Product price must be a number.")
        if price < 0:
            raise ValueError("Product price cannot be negative.")
        self.__product_price = float(price)

    # ── Create: Save a new product ──────────────────────────

    def save(self):
        """Insert this product into the database."""
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
                str(self.product_prices),  # Store as JSON/text if DB doesn't support arrays
                self.__product_price,
                self.product_description,
            ),
        )
        db.close()

    # ── Update: Modify an existing product ──────────────────

    def update(self, product_id):
        """Update product in database."""
        db = Database()
        db.execute(
            """
            UPDATE products 
            SET product_image=%s, product_name=%s, product_prices=%s, 
                product_price=%s, product_description=%s
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

    # ── Class Method: Build from DB data ────────────────────

    @classmethod
    def from_db(cls, data):
        """Create a Product object from database dictionary."""
        if data is None:
            return None
        
        product = cls(
            product_image=data.get("product_image"),
            product_name=data.get("product_name"),
            product_prices=data.get("product_prices"),
            product_price=data.get("product_price"),
            product_description=data.get("product_description"),
        )
        return product

    # ── Magic Methods ───────────────────────────────────────

    def __str__(self):
        return f"Product(name={self.product_name}, price={self.__product_price})"

    def __repr__(self):
        return f"<Product name={self.product_name}>"

    def __eq__(self, other):
        if isinstance(other, Product):
            return self.product_name == other.product_name
        return False