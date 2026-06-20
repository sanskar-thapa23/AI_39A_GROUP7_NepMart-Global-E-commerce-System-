from flask import flash, redirect, render_template, request, session, url_for, current_app
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadTimeSignature
from app.controller.basecontroller import BaseController
from app.model.usermodel import User
from app.model.database import Database

class AuthController(BaseController):

    def __init__(self):
        self.user_model = User()

    # =====================================================
    # LOGIN
    # =====================================================
    def login(self):

        if self.is_logged_in():
            return redirect(url_for("main.dashboard"))

        if request.method == "POST":

            username, password = self.get_form_data("username", "password")

            if not username or not password:
                flash("Username and password are required.", "danger")
                return render_template("auth/login.html")

            user_data = self.user_model.find_by("username", username)

            if user_data:
                user = User.from_db(user_data)

                if user.check_password(password):

                    session["user_id"] = user_data["id"]
                    session["user_name"] = user_data["username"]
                    session["role"] = user_data["role"]

                    role = user_data["role"]

                    flash("Login successful!", "success")

                    # =================================================
                    # ROLE ROUTING (IMPORTANT FIX)
                    # =================================================
                    if role == "vendor":
                        return redirect(url_for("vendor.dashboard"))

                    elif role == "customer":
                        return redirect(url_for("main.dashboard"))

                    elif role == "admin":
                        return redirect(url_for("main.dashboard"))

            flash("Invalid username or password.", "danger")

        return render_template("auth/login.html")

    # =====================================================
    # REGISTER
    # =====================================================
    def register(self):

        if self.is_logged_in():
            return redirect(url_for("main.dashboard"))

        if request.method == "POST":

            username = request.form.get("username", "").strip()
            email = request.form.get("email", "").strip()
            password = request.form.get("password", "")
            confirm_password = request.form.get("confirm_password", "")
            role = request.form.get("role", "customer")

            if not username or not email or not password or not confirm_password:
                flash("All fields are required.", "danger")
                return render_template("auth/register.html")

            if password != confirm_password:
                flash("Passwords do not match.", "danger")
                return render_template("auth/register.html")

            allowed_roles = ["customer", "vendor"]
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
                return render_template("auth/register.html")

            if new_user.username_exists():
                flash("Username already exists.", "danger")
                return render_template("auth/register.html")

            new_user.save()

            flash("Registration successful! Please login.", "success")
            return redirect(url_for("auth.login"))

        return render_template("auth/register.html")

    # =====================================================
    # FORGOT PASSWORD
    # =====================================================
    def forgot_password(self):
        """Handles the forgot password request flow."""
        if self.is_logged_in():
            return redirect(url_for("main.dashboard"))

        if request.method == "POST":
            email = request.form.get("email", "").strip()

            if not email:
                flash("Corporate email is required.", "danger")
                return render_template("auth/forgot_password.html")

            # Check if user exists with this email (using inherited BaseModel functionality)
            user_data = self.user_model.find_by("email", email)

            if user_data:
                # 1. Generate a secure token (valid for 30 minutes)
                serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
                token = serializer.dumps(email, salt="password-reset-salt")
                
                # 2. Create the reset link
                reset_url = url_for("auth.reset_password", token=token, _external=True)
                
                mail = current_app.extensions.get("mail")
                if mail:
                    # 3. Send the actual recovery email
                    msg = Message(
                        "Password Reset Request — Nep-Mart Global",
                        sender=current_app.config.get("MAIL_DEFAULT_SENDER"),
                        recipients=[email],
                        body=f"Hello,\n\nTo reset your password, please click the link below:\n{reset_url}\n\nIf you did not request this, please ignore this email.\n\nBest regards,\nNep-Mart Global Team"
                    )
                    try:
                        mail.send(msg)
                    except Exception as e:
                        print(f"Error sending email: {e}")
                        flash("There was an error sending the recovery email. Please try again later.", "danger")
                        return render_template("auth/forgot_password.html")
                else:
                    print(f"Warning: Mail extension not initialized. Reset Link: {reset_url}")

                return self.flash_and_redirect("If that email is registered, recovery instructions have been sent.", "success", "auth.login")
            
            # We use the same message for security (don't reveal if email exists or not)
            return self.flash_and_redirect("If that email is registered, recovery instructions have been sent.", "success", "auth.login")

        return render_template("auth/forgot_password.html")

    # =====================================================
    # RESET PASSWORD
    # =====================================================
    def reset_password(self, token):
        """Handles the actual password update via token."""
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        
        try:
            # Token expires in 1800 seconds (30 minutes)
            email = serializer.loads(token, salt="password-reset-salt", max_age=1800)
        except (SignatureExpired, BadTimeSignature):
            flash("The reset link is invalid or has expired.", "danger")
            return redirect(url_for("auth.forgot_password"))

        if request.method == "POST":
            password, confirm_password = self.get_form_data("password", "confirm_password")

            if not password or password != confirm_password:
                flash("Passwords must match and cannot be empty.", "danger")
                return render_template("auth/reset_password.html", token=token)

            # Update the user's password in the database
            user_data = self.user_model.find_by("email", email)
            if user_data:
                user = User.from_db(user_data)
                user.set_password(password)
                # We use the existing update_profile logic to save the new hash
                user.update_profile(user_data['id'], update_password=True)
                
                flash("Your password has been reset successfully!", "success")
                return redirect(url_for("auth.login"))

        return render_template("auth/reset_password.html", token=token)

    # =====================================================
    # DASHBOARD (NOT USED DIRECTLY NOW)
    # =====================================================
    def dashboard(self):
        return render_template("dashboard.html")

    # =====================================================
    # LOGOUT
    # =====================================================
    def logout(self):
        session.clear()
        return redirect(url_for("auth.login"))