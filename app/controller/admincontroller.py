from flask import render_template, flash, redirect, url_for, request
from app.controller.basecontroller import BaseController
from app.model.usermodel import User
from app.model.database import Database

class AdminController(BaseController):
    def __init__(self):
        self.user_model = User()

    def index(self):
        """Fetch all users and display them in the admin dashboard."""
        # find_all is inherited from BaseModel
        users = self.user_model.find_all(order_by="id DESC")
        return render_template("admin/index.html", users=users)

    def edit_user(self, user_id):
        """Update user details including role and contact info."""
        user_data = self.user_model.find_by_id(user_id)
        if not user_data:
            flash("User not found.", "danger")
            return redirect(url_for("admin.index"))

        if request.method == "POST":
            username, email, role = self.get_form_data("username", "email", "role")
            
            if not username or not email or not role:
                flash("All fields are required.", "danger")
                return render_template("admin/edit.html", user=user_data)

            db = Database()
            db.execute(
                "UPDATE users SET username = %s, email = %s, role = %s WHERE id = %s",
                (username, email, role, user_id)
            )
            db.close()
            
            flash(f"User '{username}' updated successfully.", "success")
            return redirect(url_for("admin.index"))

        return render_template("admin/edit.html", user=user_data)

    def delete_user(self, user_id):
        """Delete a user from the system."""
        current_admin_id = self.get_current_user_id()
        
        if int(user_id) == int(current_admin_id):
            flash("Security alert: You cannot delete your own account.", "danger")
        else:
            # delete_by_id is inherited from BaseModel
            self.user_model.delete_by_id(user_id)
            flash("User has been removed successfully.", "success")
            
        return redirect(url_for("admin.index"))