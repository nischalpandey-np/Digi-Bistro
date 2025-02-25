from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import get_user, save_user
from werkzeug.security import check_password_hash, generate_password_hash
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully!', 'success')
            next_url = request.args.get('next', url_for('view_menu'))
            return redirect(next_url)
        flash('Invalid username or password.', 'error')
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Validate fields
        if not all([first_name, last_name, username, email, password]):
            flash('All fields are required.', 'error')
            return redirect(url_for('auth.register'))

        # Basic email validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Please enter a valid email address.', 'error')
            return redirect(url_for('auth.register'))

        # Check if username or email already exists
        if get_user(username):
            flash('Username already exists.', 'error')
            return redirect(url_for('auth.register'))

        user_id = save_user(first_name, last_name, username, email, password)
        if user_id:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        flash('Registration failed. Please try again.', 'error')
    return render_template('register.html')