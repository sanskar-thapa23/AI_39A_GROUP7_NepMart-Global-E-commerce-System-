"""
=============================================================
  NepMart — Buyer Controller
=============================================================
  Cart management, checkout, order history.
=============================================================
"""

from flask import (
    flash, redirect, render_template, request, session, url_for, abort, jsonify
)
from app.controller.basecontroller import BaseController
from app.model.cart import Cart
from app.model.order import Order
from app.model.product import Product


class BuyerController(BaseController):

    # ── CART ─────────────────────────────────────────────────────

    def view_cart(self):
        if not self.is_logged_in():
            flash("Please log in to view your cart.", "danger")
            return redirect(url_for("auth.login"))

        user_id = self.get_current_user_id()
        items   = Cart.get_items(user_id)
        total   = Cart.get_total(user_id)

        return render_template(
            "buyer/cart.html",
            cart_items=items,
            cart_total=total,
            active_page="cart",
        )

    def add_to_cart(self, product_id):
        if not self.is_logged_in():
            flash("Please log in to add items to cart.", "danger")
            return redirect(url_for("auth.login"))

        product = Product.get_by_id(product_id)
        if not product:
            abort(404)

        quantity = int(request.form.get("quantity", 1))
        if quantity < 1:
            quantity = 1

        Cart.add(self.get_current_user_id(), product_id, quantity)
        flash(f'"{product["name"]}" added to cart!', "success")

        next_url = request.form.get("next") or request.referrer or url_for("main.products")
        return redirect(next_url)

    def remove_from_cart(self, product_id):
        if not self.is_logged_in():
            return redirect(url_for("auth.login"))

        Cart.remove(self.get_current_user_id(), product_id)
        flash("Item removed from cart.", "success")
        return redirect(url_for("buyer.cart"))

    def update_cart(self):
        if not self.is_logged_in():
            return redirect(url_for("auth.login"))

        cart_id  = request.form.get("cart_id")
        quantity = int(request.form.get("quantity", 1))
        Cart.update_quantity(int(cart_id), quantity)
        return redirect(url_for("buyer.cart"))

    # ── CHECKOUT ─────────────────────────────────────────────────

    def checkout(self):
        if not self.is_logged_in():
            flash("Please log in to checkout.", "danger")
            return redirect(url_for("auth.login"))

        user_id = self.get_current_user_id()
        items   = Cart.get_items(user_id)

        if not items:
            flash("Your cart is empty.", "danger")
            return redirect(url_for("buyer.cart"))

        if request.method == "POST":
            # Create one order per cart item
            for item in items:
                order = Order(
                    buyer_id=user_id,
                    seller_id=item["seller_id"],
                    product_id=item["product_id"],
                    quantity=item["quantity"],
                    total_amount=float(item["subtotal"]),
                    order_status="pending",
                )
                order.save()

            # Clear cart after successful checkout
            Cart.clear(user_id)
            flash("Order placed successfully! Sellers will contact you shortly.", "success")
            return redirect(url_for("buyer.orders"))

        total = Cart.get_total(user_id)
        return render_template(
            "buyer/checkout.html",
            cart_items=items,
            cart_total=total,
            active_page="cart",
        )

    # ── MY ORDERS ────────────────────────────────────────────────

    def my_orders(self):
        if not self.is_logged_in():
            flash("Please log in to view your orders.", "danger")
            return redirect(url_for("auth.login"))

        orders = Order.get_by_buyer(self.get_current_user_id())
        return render_template(
            "buyer/orders.html",
            orders=orders,
            active_page="orders",
        )
