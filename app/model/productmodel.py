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
        stock=0,
        product_description=None,
        rating=0,
        reviews_count=0,
        id=None,
        vendor_id=None,
        vendor_name=None,
    ):
        self.id = id
        self.vendor_id = vendor_id
        self.vendor_name = vendor_name
        self.product_image = product_image
        self.product_name = product_name
        self.product_prices = product_prices or []
        self.category = category
        self.location = location
        self.stock = stock
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

    # ---------------- COMPATIBILITY PROPERTIES ----------------
    @property
    def name(self):
        return self.product_name

    @property
    def description(self):
        return self.product_description

    @property
    def company(self):
        return self.vendor_name or "NepMart Partner"

    @property
    def price_range(self):
        return f"Rs. {self.product_price}"

    @property
    def moq(self):
        return "1 Unit"

    @property
    def specs(self):
        return {
            "packing": "Standard Export Packing",
            "certification": "Verified Seller Guarantee",
            "freight": "Global cargo shipping available",
            "hscode": "8437.80.00 (General Code)"
        }

    @property
    def category_display(self):
        mapping = {
            'Agro': 'Himalayan Agro & Herbs',
            'Crafts': 'Handmade Crafts',
            'Industrial': 'Industrial Machinery',
            'Logistics': 'Trade Logistics'
        }
        return mapping.get(self.category, self.category or 'General Sourcing')

    # ---------------- RECOMMENDATION QUERIES ----------------
    @classmethod
    def get_trending(cls, limit=4):
        """Fetch trending products based on view count."""
        db = Database()
        query = """
            SELECT p.*, u.username AS vendor_name, COUNT(pv.id) AS view_count
            FROM products p
            LEFT JOIN user_products up ON p.id = up.product_id
            LEFT JOIN users u ON up.user_id = u.id
            LEFT JOIN product_views pv ON p.id = pv.product_id
            GROUP BY p.id, u.username
            ORDER BY view_count DESC
            LIMIT %s
        """
        results = db.fetch_all(query, (limit,))
        db.close()
        return [cls.from_db(item) for item in results]

    @classmethod
    def get_content_based(cls, category, exclude_id, limit=4):
        """Fetch similar products based on the category."""
        db = Database()
        query = """
            SELECT p.*, u.username AS vendor_name
            FROM products p
            LEFT JOIN user_products up ON p.id = up.product_id
            LEFT JOIN users u ON up.user_id = u.id
            WHERE p.category = %s AND p.id != %s
            ORDER BY p.id DESC
            LIMIT %s
        """
        results = db.fetch_all(query, (category, exclude_id, limit))
        db.close()
        return [cls.from_db(item) for item in results]

    @classmethod
    def get_collaborative(cls, user_id, limit=4):
        """Fetch collaborative filtering recommendations for a logged in user."""
        db = Database()
        # Find products viewed by users who have viewed the same products as user_id,
        # but which user_id has not yet viewed.
        query = """
            SELECT p.*, u.username AS vendor_name, COUNT(pv2.id) AS recommendation_strength
            FROM product_views pv1
            JOIN product_views pv2 ON pv1.product_id = pv2.product_id
            JOIN products p ON pv2.product_id = p.id
            LEFT JOIN user_products up ON p.id = up.product_id
            LEFT JOIN users u ON up.user_id = u.id
            WHERE pv1.user_id = %s 
              AND pv2.user_id != %s
              AND pv2.product_id NOT IN (
                  SELECT product_id FROM product_views WHERE user_id = %s
              )
            GROUP BY p.id, u.username
            ORDER BY recommendation_strength DESC
            LIMIT %s
        """
        results = db.fetch_all(query, (user_id, user_id, user_id, limit))
        
        # If not enough collaborative recommendations, fall back to trending
        if len(results) < limit:
            db.close()
            trending = cls.get_trending(limit=limit)
            # Merge lists ensuring unique products
            existing_ids = {item['id'] for item in results} if results else set()
            for prod in trending:
                if prod.id not in existing_ids and len(results) < limit:
                    results.append({
                        'id': prod.id,
                        'vendor_id': prod.vendor_id,
                        'vendor_name': prod.vendor_name,
                        'product_image': prod.product_image,
                        'product_name': prod.product_name,
                        'product_price': prod.product_price,
                        'stock': prod.stock,
                        'category': prod.category,
                        'location': prod.location,
                        'product_description': prod.product_description,
                        'rating': prod.rating,
                        'reviews_count': prod.reviews_count
                    })
            return [cls.from_db(item) for item in results]
            
        db.close()
        return [cls.from_db(item) for item in results]

    @classmethod
    def get_recently_viewed(cls, user_id, limit=4):
        """Fetch recently viewed products by the user."""
        db = Database()
        query = """
            SELECT p.*, u.username AS vendor_name, MAX(pv.viewed_at) as last_viewed
            FROM product_views pv
            JOIN products p ON pv.product_id = p.id
            LEFT JOIN user_products up ON p.id = up.product_id
            LEFT JOIN users u ON up.user_id = u.id
            WHERE pv.user_id = %s
            GROUP BY p.id, u.username
            ORDER BY last_viewed DESC
            LIMIT %s
        """
        results = db.fetch_all(query, (user_id, limit))
        db.close()
        return [cls.from_db(item) for item in results]

    @classmethod
    def get_frequently_bought_together(cls, product_id, limit=4):
        """Fetch products that are frequently bought by users who also bought product_id."""
        db = Database()
        query = """
            SELECT p.*, u.username AS vendor_name, COUNT(o2.id) AS purchase_frequency
            FROM orders o1
            JOIN orders o2 ON o1.user_id = o2.user_id
            JOIN products p ON o2.product_id = p.id
            LEFT JOIN user_products up ON p.id = up.product_id
            LEFT JOIN users u ON up.user_id = u.id
            WHERE o1.product_id = %s 
              AND o2.product_id != %s
            GROUP BY p.id, u.username
            ORDER BY purchase_frequency DESC
            LIMIT %s
        """
        results = db.fetch_all(query, (product_id, product_id, limit))
        
        # Fallback to similar category products if no purchase history exists
        if not results:
            db.close()
            # Fetch current product details to get category
            db = Database()
            product_data = db.fetch_one("SELECT category FROM products WHERE id = %s", (product_id,))
            category = product_data['category'] if product_data else None
            db.close()
            return cls.get_content_based(category, product_id, limit)
            
        db.close()
        return [cls.from_db(item) for item in results]

    @classmethod
    def get_based_on_preferences(cls, user_id, limit=4):
        """Fetch products based on the user's most-viewed category (preference-based)."""
        db = Database()
        # Find the user's most frequently viewed category
        pref_query = """
            SELECT p.category, COUNT(*) AS freq
            FROM product_views pv
            JOIN products p ON pv.product_id = p.id
            WHERE pv.user_id = %s AND p.category IS NOT NULL
            GROUP BY p.category
            ORDER BY freq DESC
            LIMIT 1
        """
        preferred_category = db.fetch_one(pref_query, (user_id,))
        db.close()

        if not preferred_category:
            # Fallback: return trending if user has no view history
            return cls.get_trending(limit=limit)

        category = preferred_category['category']
        # Fetch top products in that category (excluding already viewed)
        db = Database()
        query = """
            SELECT p.*, u.username AS vendor_name
            FROM products p
            LEFT JOIN user_products up ON p.id = up.product_id
            LEFT JOIN users u ON up.user_id = u.id
            WHERE p.category = %s
              AND p.id NOT IN (
                  SELECT product_id FROM product_views WHERE user_id = %s
              )
            ORDER BY p.id DESC
            LIMIT %s
        """
        results = db.fetch_all(query, (category, user_id, limit))
        db.close()

        # If all category products already seen, return without exclusion filter
        if not results:
            db = Database()
            query_fallback = """
                SELECT p.*, u.username AS vendor_name
                FROM products p
                LEFT JOIN user_products up ON p.id = up.product_id
                LEFT JOIN users u ON up.user_id = u.id
                WHERE p.category = %s
                ORDER BY p.id DESC
                LIMIT %s
            """
            results = db.fetch_all(query_fallback, (category, limit))
            db.close()

        return [cls.from_db(item) for item in results], category

    @classmethod
    def get_homepage_frequently_bought(cls, user_id=None, limit=4):
        """
        For homepage: if user is logged in, find products frequently purchased
        alongside items in their order history. Otherwise, return globally popular
        cross-purchases.
        """
        db = Database()
        if user_id:
            query = """
                SELECT p.*, u.username AS vendor_name, COUNT(o2.id) AS purchase_frequency
                FROM orders o1
                JOIN orders o2 ON o1.user_id = o2.user_id AND o2.product_id != o1.product_id
                JOIN products p ON o2.product_id = p.id
                LEFT JOIN user_products up ON p.id = up.product_id
                LEFT JOIN users u ON up.user_id = u.id
                WHERE o1.user_id = %s
                GROUP BY p.id, u.username
                ORDER BY purchase_frequency DESC
                LIMIT %s
            """
            results = db.fetch_all(query, (user_id, limit))
        else:
            results = []

        # Fallback to global trending cross-purchases if no user history
        if not results:
            db.close()
            db = Database()
            query_global = """
                SELECT p.*, u.username AS vendor_name, COUNT(o2.id) AS purchase_frequency
                FROM orders o1
                JOIN orders o2 ON o1.user_id = o2.user_id AND o2.product_id != o1.product_id
                JOIN products p ON o2.product_id = p.id
                LEFT JOIN user_products up ON p.id = up.product_id
                LEFT JOIN users u ON up.user_id = u.id
                GROUP BY p.id, u.username
                ORDER BY purchase_frequency DESC
                LIMIT %s
            """
            results = db.fetch_all(query_global, (limit,))
            db.close()
            return [cls.from_db(item) for item in results]

        db.close()
        return [cls.from_db(item) for item in results]


    # ---------------- CREATE ----------------
    def save(self, user_id):

        db = Database()

        db.execute(
            """
            INSERT INTO products
            (vendor_id, product_image, product_name, product_prices, product_price, stock, category, location, product_description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                self.product_image,
                self.product_name,
                str(self.product_prices),
                self.__product_price,
                self.stock,
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
            SET vendor_id=%s,
                product_image=%s,
                product_name=%s,
                product_prices=%s,
                product_price=%s,
                stock=%s,
                category=%s,
                location=%s,
                product_description=%s
            WHERE id=%s
            """,
            (
                self.vendor_id,
                self.product_image,
                self.product_name,
                str(self.product_prices),
                self.__product_price,
                self.stock,
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
            stock=data.get("stock", 0),
            rating=data.get("rating", 0),
            reviews_count=data.get("reviews_count", 0),
            product_description=data.get("product_description"),
            id=data.get("id"),
            vendor_id=data.get("vendor_id"),
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