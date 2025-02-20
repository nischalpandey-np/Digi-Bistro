from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import mysql.connector
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

auth_bp = Blueprint('auth', __name__)

# MySQL Configuration
DB_CONFIG = {
    "host": os.getenv('DB_HOST', 'localhost'),
    "user": os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD', ''),
    "database": os.getenv('DB_NAME', 'gourmetBistro_db')
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Create users table if not exists
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute(''' 
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        first_name VARCHAR(50) NOT NULL,
        last_name VARCHAR(50) NOT NULL,
        email VARCHAR(100) NOT NULL
    )
''')
conn.commit()
cursor.close()
conn.close()

@auth_bp.route('/register', methods=['GET'])
def register_page():
    return render_template('auth/register.html')

@auth_bp.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')

    # Hash the password before storing it
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO users (username, password, first_name, last_name, email)
            VALUES (%s, %s, %s, %s, %s)
        ''', (username, hashed_password, first_name, last_name, email))
        conn.commit()
        flash("Registration successful. Please log in.", "success")
        return redirect(url_for('auth.login_page'))
    except mysql.connector.IntegrityError:
        flash("Username already exists, please choose another.", "error")
        return redirect(url_for('auth.register_page'))
    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('auth/login.html')

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    user = authenticate_user(username, password)

    if user:
        session['user_id'] = user['id']
        flash("Login successful.", "success")
        # Redirect to order page by default
        next_page = request.args.get('next', url_for('order'))
        return redirect(next_page)
    else:
        flash("Invalid credentials", "error")
        return redirect(url_for('auth.login_page'))

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('index'))

def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        return user
    return None
