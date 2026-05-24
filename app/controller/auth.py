from flask import render_template, redirect, url_for, flash, request

from app.model.user import User


class AuthController:

    def __init__(self):
        self.user_model = User()

    # LOGIN
    def login(self):

        if request.method == 'POST':

            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')

            error = None

            # Get user from database
            user = self.user_model.get_user_by_username(username)

            if not user:
                error = 'Invalid username or password.'

            elif not self.user_model.check_password(
                user['password_hash'],
                password
            ):
                error = 'Invalid username or password.'

            if error:
                flash(error, 'danger')
                return render_template('auth/login.html')

            flash(
                f"Welcome back, {user['username']}! "
                f"Logged in as {user['role'].capitalize()}.",
                'success'
            )

            if user['role'] == 'admin':
                return redirect(url_for('admin.dashboard'))

            return redirect(url_for('home.index'))

        return render_template('auth/login.html')

    # REGISTER
    def register(self):

        if request.method == 'POST':

            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm = request.form.get('confirm_password', '')
            role = request.form.get('role', 'customer').strip().lower()

            error = None

            # Validation
            if not username or not email or not password:
                error = 'All fields are required.'

            elif len(username) < 3:
                error = 'Username must be at least 3 characters.'

            elif len(password) < 6:
                error = 'Password must be at least 6 characters.'

            elif password != confirm:
                error = 'Passwords do not match.'

            elif role not in ['customer', 'manager', 'admin']:
                error = 'Invalid user role selected.'

            elif self.user_model.get_user_by_username(username):
                error = f'Username "{username}" is already taken.'

            elif self.user_model.get_user_by_email(email):
                error = 'An account with that email already exists.'

            if error:
                flash(error, 'danger')
                return render_template('auth/register.html')  # FIXED: was 'landing_page.html'

            # Create user
            self.user_model.create_user(
                username=username,
                email=email,
                password=password,
                role=role
            )

            flash(
                f'Account created successfully as a {role}! Please log in.',
                'success'
            )

            return render_template("login.html")

        return render_template('auth/register.html')