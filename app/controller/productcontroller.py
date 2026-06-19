
from flask import flash, redirect, render_template, request, url_for
from app.controller.basecontroller import BaseController
from app.model.productmodel import Product
from app.model.database import Database


class ProductController(BaseController):

    def __init__(self):
        self.product_model = Product()

    # =====================================================
    # READ ALL PRODUCTS + SEARCH + SORT + FILTER
    # =====================================================
    def index(self):

        db = Database()

        # ---------------- GET QUERY PARAMETERS ----------------
        search = request.args.get("search", "").strip()
        sort = request.args.get("sort", "").strip()
        categories = request.args.getlist("category")
        locations = request.args.getlist("location")

        # ---------------- BASE QUERY WITH VENDOR JOIN ----------------
        query = """
            SELECT p.*, u.username AS vendor_name 
            FROM products p
            LEFT JOIN user_products up ON p.id = up.product_id
            LEFT JOIN users u ON up.user_id = u.id
            WHERE 1=1
        """
        params = []

        # =====================================================
        # SEARCHING
        # =====================================================
        if search:
            query += " AND p.product_name LIKE %s"
            params.append(f"%{search}%")

        # =====================================================
        # FILTERING
        # =====================================================

        if categories:
            placeholders = ', '.join(['%s'] * len(categories))
            query += f" AND p.category IN ({placeholders})"
            params.extend(categories)

        if locations:
            placeholders = ', '.join(['%s'] * len(locations))
            query += f" AND p.location IN ({placeholders})"
            params.extend(locations)

        # =====================================================
        # SORTING
        # =====================================================

        # Lowest price first
        if sort == "low":
            query += " ORDER BY p.product_price ASC"

        # Highest price first
        elif sort == "high":
            query += " ORDER BY p.product_price DESC"

        # Alphabetical order
        elif sort == "name":
            query += " ORDER BY p.product_name ASC"

        # Latest products first
        else:
            query += " ORDER BY p.id DESC"

        # =====================================================
        # FETCH PRODUCTS
        # =====================================================
        products_data = db.fetch_all(query, tuple(params))

        db.close()

        # Convert DB rows into Product objects
        products = [
            Product.from_db(product)
            for product in products_data
        ]

        return render_template(
            "products.html",
            products=products,
            search_query=search,
            sort=sort,
            selected_categories=categories,
            selected_locations=locations
        )

    # =====================================================
    # READ SINGLE PRODUCT
    # =====================================================
    def detail(self, product_id):
        db = Database()
        product_data = db.fetch_one(
            """
            SELECT p.*, u.username AS vendor_name, u.email AS vendor_email
            FROM products p 
            LEFT JOIN user_products up ON p.id = up.product_id 
            LEFT JOIN users u ON up.user_id = u.id 
            WHERE p.id=%s
            """,
            (product_id,)
        )
        db.close()

        if not product_data:
            return self.flash_and_redirect(
                "Product not found.",
                "danger",
                "vendor.dashboard"
            )

        product = Product.from_db(product_data)
        product.vendor_email = product_data.get('vendor_email')

        # 2. Track view (User Story 2.1)
        user_id = self.get_current_user_id()
        from app.model.product_view import ProductView
        view = ProductView(user_id=user_id, product_id=product_id)
        view.save()

        # 3. Fetch similar products (User Story 2.2 Content-Based)
        similar_products = Product.get_content_based(product.category, product.id, limit=4)

        # 4. Fetch frequently bought together products (User Story 2.5)
        frequently_bought = Product.get_frequently_bought_together(product.id, limit=4)

        return render_template(
            "product_detail.html",
            product=product,
            similar_products=similar_products,
            frequently_bought=frequently_bought
        )

    # =====================================================
    # SHOPPING ACTIONS
    # =====================================================
    def add_to_cart(self, product_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.flash_and_redirect("Please login to shop.", "danger", "auth.login")

        db = Database()
        try:
            existing = db.fetch_one(
                "SELECT id, quantity FROM shopping_cart WHERE user_id = %s AND product_id = %s",
                (user_id, product_id)
            )
            if existing:
                db.execute(
                    "UPDATE shopping_cart SET quantity = quantity + 1 WHERE id = %s",
                    (existing['id'],)
                )
            else:
                db.execute(
                    "INSERT INTO shopping_cart (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                    (user_id, product_id, 1)
                )
            return self.flash_and_redirect("Item added to cart.", "success", "main.products")
        except Exception as e:
            return self.flash_and_redirect(str(e), "danger", "main.products")
        finally:
            db.close()

    def add_to_wishlist(self, product_id):
        user_id = self.get_current_user_id()
        if not user_id:
            return self.flash_and_redirect("Please login to save favorites.", "danger", "auth.login")

        db = Database()
        try:
            db.execute(
                "INSERT IGNORE INTO wishlist (user_id, product_id) VALUES (%s, %s)",
                (user_id, product_id)
            )
            return self.flash_and_redirect("Item added to wishlist.", "success", "main.products")
        except Exception as e:
            return self.flash_and_redirect(str(e), "danger", "main.products")
        finally:
            db.close()

    # =====================================================
    # CREATE PRODUCT
    # =====================================================
    def create(self):

        if request.method == "POST":

            try:

                # ---------------- AUTH CHECK ----------------
                user_id = self.get_current_user_id()
                if not user_id:
                    return self.flash_and_redirect(
                        "You must be logged in to list a product.",
                        "danger",
                        "auth.login"
                    )

                # ---------------- FORM DATA ----------------
                product_image = request.form.get(
                    "product_image",
                    ""
                ).strip()

                product_name = request.form.get(
                    "product_name",
                    ""
                ).strip()

                product_price = request.form.get(
                    "product_price",
                    ""
                ).strip()

                product_category = request.form.get(
                    "category",
                    ""
                ).strip()

                product_location = request.form.get(
                    "location",
                    ""
                ).strip()

                product_stock = request.form.get(
                    "stock",
                    "0"
                ).strip()

                product_description = request.form.get(
                    "product_description",
                    ""
                ).strip()

                # =====================================================
                # VALIDATION
                # =====================================================

                if not product_name:
                    flash("Product name is required.", "danger")
                    return render_template("products/create.html")

                if not product_price:
                    flash("Product price is required.", "danger")
                    return render_template("products/create.html")

                # =====================================================
                # CREATE PRODUCT OBJECT
                # =====================================================
                product = Product(
                    product_image=product_image,
                    product_name=product_name,
                    product_price=float(product_price),
                    product_description=product_description,
                    category=product_category,
                    location=product_location,
                    stock=int(product_stock) if product_stock else 0
                )

                # Save to database
                product.save(user_id)

                return self.flash_and_redirect(
                    "Product created successfully.",
                    "success",
                    "vendor.dashboard"
                )

            except ValueError:
                flash("Price must be a valid number.", "danger")

            except Exception as e:
                flash(str(e), "danger")

        return render_template("products/create.html")

    # =====================================================
    # UPDATE PRODUCT
    # =====================================================
    def edit(self, product_id):

        user_id = self.get_current_user_id()
        if not user_id:
            return self.flash_and_redirect("Login required.", "danger", "auth.login")

        db = Database()

        # Security check: Ensure only the owner (vendor) can fetch and edit this product
        product_data = db.fetch_one(
            "SELECT * FROM products WHERE id=%s AND vendor_id=%s",
            (product_id, user_id)
        )

        if not product_data:
            db.close()
            return self.flash_and_redirect(
                "Product not found or unauthorized access.",
                "danger",
                "vendor.dashboard"
            )

        product = Product.from_db(product_data)

        # =====================================================
        # UPDATE ON POST
        # =====================================================
        if request.method == "POST":

            try:

                # ---------------- UPDATE VALUES ----------------
                product.product_image = request.form.get(
                    "product_image",
                    ""
                ).strip()

                product.product_name = request.form.get(
                    "product_name",
                    ""
                ).strip()

                product.category = request.form.get(
                    "category",
                    ""
                ).strip()

                product.location = request.form.get(
                    "location",
                    ""
                ).strip()

                product.product_description = request.form.get(
                    "product_description",
                    ""
                ).strip()

                product.stock = int(request.form.get(
                    "stock",
                    0
                ))

                # Encapsulated setter
                product.set_product_price(
                    float(
                        request.form.get(
                            "product_price",
                            0
                        )
                    )
                )

                # Update database
                product.update(product_id)

                db.close()

                return self.flash_and_redirect(
                    "Product updated successfully.",
                    "success",
                    "vendor.dashboard"
                )

            except ValueError:
                flash("Price must be a valid number.", "danger")

            except Exception as e:
                flash(str(e), "danger")

        db.close()

        return render_template(
            "products/edit.html",
            product=product
        )

    # =====================================================
    # DELETE PRODUCT
    # =====================================================
    def delete(self, product_id):

        user_id = self.get_current_user_id()
        if not user_id:
            return self.flash_and_redirect("Login required.", "danger", "auth.login")

        db = Database()

        # Security check: Ensure only the owner (vendor) can delete this product
        product_data = db.fetch_one(
            "SELECT * FROM products WHERE id=%s AND vendor_id=%s",
            (product_id, user_id)
        )

        if not product_data:
            db.close()
            return self.flash_and_redirect(
                "Product not found or unauthorized access.",
                "danger",
                "vendor.dashboard"
            )

        # Delete product
        db.execute(
            "DELETE FROM products WHERE id=%s",
            (product_id,)
        )

        db.close()

        return self.flash_and_redirect(
            "Product deleted successfully.",
            "success",
            "vendor.dashboard"
        )
