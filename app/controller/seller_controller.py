"""
=============================================================
  NepMart — Seller Controller
=============================================================
  Full seller dashboard: products CRUD, orders, analytics,
  profile management.
=============================================================
"""

from flask import (
    flash, redirect, render_template, request, session, url_for, abort
)
from app.controller.basecontroller import BaseController
from app.model.product import Product
from app.model.seller import Seller
from app.model.order import Order
from app.services.upload_service import save_product_image, delete_product_image
from app.services.auth_service import seller_required


class SellerController(BaseController):

    def _get_seller_id(self):
        sid = session.get("seller_id")
        if not sid:
            seller = Seller.find_by_user_id(session.get("user_id"))
            if seller:
                session["seller_id"] = seller["seller_id"]
                sid = seller["seller_id"]
        return sid

    # ── DASHBOARD ────────────────────────────────────────────────

    def dashboard(self):
        seller_id = self._get_seller_id()
        if not seller_id:
            flash("Seller profile not found.", "danger")
            return redirect(url_for("auth.logout"))

        seller  = Seller.get_with_user(seller_id)
        stats   = Seller.get_dashboard_stats(seller_id)
        products = Product.get_by_seller(seller_id)[:5]  # recent 5
        orders   = Order.get_by_seller(seller_id)[:5]    # recent 5

        return render_template(
            "seller/dashboard.html",
            seller=seller,
            stats=stats,
            recent_products=products,
            recent_orders=orders,
            active_page="seller_dashboard",
        )

    # ── PRODUCTS LIST ────────────────────────────────────────────

    def products(self):
        seller_id = self._get_seller_id()
        products  = Product.get_by_seller(seller_id)
        return render_template(
            "seller/products.html",
            products=products,
            active_page="seller_dashboard",
        )

    # ── ADD PRODUCT ──────────────────────────────────────────────

    def add_product(self):
        seller_id = self._get_seller_id()

        if request.method == "POST":
            name        = request.form.get("name", "").strip()
            category    = request.form.get("category", "").strip()
            description = request.form.get("description", "").strip()
            price_str   = request.form.get("price", "0").strip()
            stock_str   = request.form.get("stock", "0").strip()
            image_file  = request.files.get("image")

            if not name or not category or not price_str:
                flash("Name, category, and price are required.", "danger")
                return render_template("seller/add_product.html", active_page="seller_dashboard")

            try:
                price = float(price_str)
                stock = int(stock_str)
            except ValueError:
                flash("Price and stock must be valid numbers.", "danger")
                return render_template("seller/add_product.html", active_page="seller_dashboard")

            image_path = save_product_image(image_file)

            product = Product(
                seller_id=seller_id,
                name=name,
                category=category,
                description=description,
                price=price,
                stock=stock,
                image=image_path,
            )
            product.save()
            flash(f'"{name}" has been listed on the marketplace!', "success")
            return redirect(url_for("seller.products"))

        return render_template("seller/add_product.html", active_page="seller_dashboard")

    # ── EDIT PRODUCT ─────────────────────────────────────────────

    def edit_product(self, product_id):
        seller_id = self._get_seller_id()

        # Verify ownership
        from app.model.database import Database
        db = Database()
        prod_row = db.fetch_one(
            "SELECT * FROM products WHERE product_id=%s AND seller_id=%s",
            (product_id, seller_id)
        )
        db.close()

        if not prod_row:
            abort(403)

        if request.method == "POST":
            name        = request.form.get("name", "").strip()
            category    = request.form.get("category", "").strip()
            description = request.form.get("description", "").strip()
            price_str   = request.form.get("price", "0").strip()
            stock_str   = request.form.get("stock", "0").strip()
            image_file  = request.files.get("image")

            try:
                price = float(price_str)
                stock = int(stock_str)
            except ValueError:
                flash("Price and stock must be valid numbers.", "danger")
                return render_template("seller/edit_product.html",
                                       product=prod_row, active_page="seller_dashboard")

            # Handle image replacement
            image_path = prod_row.get("image")
            new_image  = save_product_image(image_file)
            if new_image:
                delete_product_image(image_path)
                image_path = new_image

            p = Product(
                seller_id=seller_id,
                name=name,
                category=category,
                description=description,
                price=price,
                stock=stock,
                image=image_path,
            )
            p.update(product_id)
            flash(f'"{name}" updated successfully.', "success")
            return redirect(url_for("seller.products"))

        return render_template(
            "seller/edit_product.html",
            product=prod_row,
            active_page="seller_dashboard",
        )

    # ── DELETE PRODUCT ───────────────────────────────────────────

    def delete_product(self, product_id):
        seller_id = self._get_seller_id()

        from app.model.database import Database
        db = Database()
        prod_row = db.fetch_one(
            "SELECT * FROM products WHERE product_id=%s AND seller_id=%s",
            (product_id, seller_id)
        )
        db.close()

        if not prod_row:
            abort(403)

        p = Product()
        p.soft_delete(product_id)
        flash("Product has been removed from the marketplace.", "success")
        return redirect(url_for("seller.products"))

    # ── ORDERS ───────────────────────────────────────────────────

    def orders(self):
        seller_id = self._get_seller_id()
        orders    = Order.get_by_seller(seller_id)
        return render_template(
            "seller/orders.html",
            orders=orders,
            active_page="seller_dashboard",
        )

    def update_order_status(self, order_id):
        """AJAX-friendly status update."""
        status = request.form.get("status", "").strip()
        if status in Order.VALID_STATUSES:
            Order.update_status(order_id, status)
            flash("Order status updated.", "success")
        return redirect(url_for("seller.orders"))

    # ── ANALYTICS ────────────────────────────────────────────────

    def analytics(self):
        seller_id = self._get_seller_id()
        stats     = Seller.get_dashboard_stats(seller_id)
        analytics = Product.get_analytics_for_seller(seller_id)
        return render_template(
            "seller/analytics.html",
            stats=stats,
            analytics=analytics,
            active_page="seller_dashboard",
        )

    # ── PROFILE ──────────────────────────────────────────────────

    def profile(self):
        seller_id = self._get_seller_id()
        seller    = Seller.get_with_user(seller_id)

        if request.method == "POST":
            business_name    = request.form.get("business_name", "").strip()
            whatsapp_number  = request.form.get("whatsapp_number", "").strip()
            business_phone   = request.form.get("business_phone", "").strip()
            business_address = request.form.get("business_address", "").strip()

            s = Seller(
                business_name=business_name,
                whatsapp_number=whatsapp_number,
                business_phone=business_phone,
                business_address=business_address,
            )
            s.update(seller_id)

            # Also update user's full_name and phone
            from app.model.usermodel import User
            full_name = request.form.get("full_name", "").strip()
            phone     = request.form.get("phone", "").strip()
            u         = User(full_name=full_name, phone=phone)
            u.update_profile(session["user_id"])
            session["user_name"] = full_name

            flash("Profile updated successfully.", "success")
            return redirect(url_for("seller.profile"))

        return render_template(
            "seller/profile.html",
            seller=seller,
            active_page="seller_dashboard",
        )
