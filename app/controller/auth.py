"""
=============================================================
  NepMart — Auth Controller
=============================================================
  Handles buyer + seller registration, login (email-based),
  logout, and role-based redirects.
=============================================================
"""

from flask import flash, redirect, render_template, request, session, url_for
from app.controller.basecontroller import BaseController
from app.model.usermodel import User
from app.model.seller import Seller


class AuthController(BaseController):

    def __init__(self):
        self.user_model = User()

    # ── LOGIN ────────────────────────────────────────────────────

    def login(self):
        if self.is_logged_in():
            return self._role_redirect()

        if request.method == "POST":
            email    = request.form.get("email", "").strip()
            password = request.form.get("password", "")

            if not email or not password:
                flash("Email and password are required.", "danger")
                return render_template("auth/login.html")

            user_data = self.user_model.find_by_email(email)

            if user_data:
                user = User.from_db(user_data)
                if user.check_password(password):
                    session["user_id"]   = user_data["id"]
                    session["user_name"] = user_data["full_name"]
                    session["role"]      = user_data["role"]

                    # Attach seller_id to session for quick access
                    if user_data["role"] == "seller":
                        seller = Seller.find_by_user_id(user_data["id"])
                        if seller:
                            session["seller_id"] = seller["seller_id"]

                    flash(f"Welcome back, {user_data['full_name']}!", "success")
                    return self._role_redirect()

            flash("Invalid email or password.", "danger")

        return render_template("auth/login.html")

    # ── REGISTER ─────────────────────────────────────────────────

    def register(self):
        if self.is_logged_in():
            return self._role_redirect()

        # Pre-fill role from query string (?role=seller)
        default_role = request.args.get("role", "buyer")

        if request.method == "POST":
            full_name        = request.form.get("full_name", "").strip()
            email            = request.form.get("email", "").strip()
            phone            = request.form.get("phone", "").strip()
            password         = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            role             = request.form.get("role", "buyer")

            # Seller-specific
            business_name    = request.form.get("business_name", "").strip()
            whatsapp_number  = request.form.get("whatsapp_number", "").strip()
            business_phone   = request.form.get("business_phone", "").strip()
            business_address = request.form.get("business_address", "").strip()

            # Validation
            if not full_name or not email or not password:
                flash("Full name, email, and password are required.", "danger")
                return render_template("auth/register.html", default_role=role)

            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("auth/register.html", default_role=role)

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("auth/register.html", default_role=role)

            if role not in ("buyer", "seller"):
                role = "buyer"

            if role == "seller" and not business_name:
                flash("Business name is required for seller registration.", "danger")
                return render_template("auth/register.html", default_role=role)

            # Check email uniqueness
            new_user = User(full_name=full_name, email=email,
                            password=password, role=role, phone_number=phone)
            if new_user.email_exists():
                flash("An account with this email already exists.", "danger")
                return render_template("auth/register.html", default_role=role)

            # Save user
            uid = new_user.save()

            # If seller, also create seller profile
            if role == "seller":
                seller = Seller(
                    user_id=uid,
                    company_name=business_name,
                    whatsapp_number=whatsapp_number,
                    business_phone=business_phone,
                    business_address=business_address,
                )
                seller.save()

            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))

        return render_template("auth/register.html", default_role=default_role)

    # ── LOGOUT ───────────────────────────────────────────────────

    def logout(self):
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for("auth.login"))

    # ── Helper ───────────────────────────────────────────────────

    def _role_redirect(self):
        role = session.get("role", "buyer")
        if role == "seller":
            return redirect(url_for("seller.dashboard"))
        elif role == "admin":
            return redirect(url_for("main.home"))
        else:
            return redirect(url_for("main.home"))