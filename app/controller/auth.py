from flask import flash, redirect, render_template, request, session, url_for
from app.controller.basecontroller import BaseController
from app.model.usermodel import User


class AuthController(BaseController):

    def __init__(self):
        self.user_model = User()

    # ---------------- LOGIN ----------------
    def login(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":
            username, password = self.get_form_data("username", "password")

            if not username or not password:
                flash("Email and password are required.", "danger")
                return render_template("auth/login.html")

            user_data = self.user_model.find_by("username", username)

            if user_data:
                user = User.from_db(user_data)

                if user.check_password(password):
                    session["user_id"] = user_data["id"]
                    session["user_name"] = user_data["username"]
                    session["role"] = user_data["role"]

                    # Role-based redirect
                    role = user_data["role"]

                    if role == "customer":
                        return render_template("customer.html")
                    elif role == "vendor":
                        return render_template("vendor.html")
                    elif role == "admin":
                        return render_template("admin.html")

            flash("Invalid email or password.", "danger")

        return render_template("auth/login.html")

    # ---------------- REGISTER ----------------
    def register(self):
        if self.is_logged_in():
            return redirect(url_for("auth.dashboard"))

        if request.method == "POST":

            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            role = request.form.get("role", "customer")

            # Validation
            if not username or not email or not password or not confirm_password:
                flash("All fields are required.", "danger")
                return render_template("auth/register.html")

            if len(username) > 100:
                flash("Username must be under 100 characters.", "danger")
                return render_template("auth/register.html")

            if len(password) < 6:
                flash("Password must be at least 6 characters.", "danger")
                return render_template("auth/register.html")

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("auth/register.html")

            allowed_roles = ["customer", "manager"]
            if role not in allowed_roles:
                role = "customer"

            new_user = User(
                username=username,
                email=email,
                password=password,
                role=role
            )

            if new_user.email_exists():
                flash("Email already exists.", "danger")
                return redirect(url_for("auth.login"))

            if new_user.username_exists():
                flash("Username already exists.", "danger")
                return render_template("auth/register.html")

            new_user.save()

            return self.flash_and_redirect(
                "Registration successful! Please login.",
                "success",
                "auth.login"
            )

        # GET request
        return render_template("auth/register.html")

    # ---------------- DASHBOARD ----------------
    def dashboard(self):
        return render_template("dashboard.html")

    # ---------------- LOGOUT ----------------
    def logout(self):
        session.clear()
        return self.flash_and_redirect(
            "Logged out Successfully",
            "success",
            "auth.login"
        )