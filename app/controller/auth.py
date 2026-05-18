from flask import render_template, redirect, url_for, flash, request
from app import db
from app.model.user import User

class AuthController:

    def login(self):
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            error = None
            user = User.query.filter_by(username=username).first()
            
            # Authentication validation incorporating role check later if needed
            if not user or not user.check_password(password):
                error = 'Invalid username or password.'
                
            if error:
                flash(error, 'danger')
                return render_template('auth/login.html')
                
            # Flash success and route according to user role
            flash(f'Welcome back, {user.username}! Logged in as {user.role.capitalize()}.', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('home.index'))

        return render_template('auth/login.html')

    def register(self):
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            email    = request.form.get('email', '').strip().lower()
            password = request.form.get('password', '')
            confirm  = request.form.get('confirm_password', '')
            
            # Extract the role from form select input, default to 'customer' for security
            role     = request.form.get('role', 'customer').strip().lower()

            error = None

            # Input validation checks
            if not username or not email or not password:
                error = 'All fields are required.'
            elif len(username) < 3:
                error = 'Username must be at least 3 characters.'
            elif len(password) < 6:
                error = 'Password must be at least 6 characters.'
            elif password != confirm:
                error = 'Passwords do not match.'
            # Restrict acceptable roles to prevent client-side form tampering/injection
            elif role not in ['customer', 'manager', 'admin']:
                error = 'Invalid user role selected.'
            elif User.query.filter_by(username=username).first():
                error = f'Username "{username}" is already taken.'
            elif User.query.filter_by(email=email).first():
                error = 'An account with that email already exists.'

            if error:
                flash(error, 'danger')
                return render_template('landing_page.html')

            # Instantiate user object, including the assigned database role string
            user = User(username=username, email=email, role=role)
            user.set_password(password)

            db.session.add(user)
            db.session.commit()

            flash(f'Account created successfully as a {role}! Please log in.', 'success')
            return render_template("login.html")

        return render_template('register.html')