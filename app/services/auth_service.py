"""
=============================================================
  NepMart — Auth Service (Decorators)
=============================================================
"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """Redirect to login if not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def buyer_required(f):
    """Restrict route to buyer role only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "danger")
            return redirect(url_for("auth.login"))
        if session.get("role") not in ("buyer", "admin"):
            flash("This area is for buyers only.", "danger")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return decorated


def seller_required(f):
    """Restrict route to seller role only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to continue.", "danger")
            return redirect(url_for("auth.login"))
        if session.get("role") not in ("seller", "admin"):
            flash("This area is for sellers only. Please register as a seller.", "danger")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    """Restrict route to admin only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session or session.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("main.home"))
        return f(*args, **kwargs)
    return decorated
