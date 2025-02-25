import mysql.connector
import os
from dotenv import load_dotenv
import logging
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "gourmet_bistro")
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection failed: {err}")
        return None

def create_tables():
    conn = get_db_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                          id INT AUTO_INCREMENT PRIMARY KEY,
                          first_name VARCHAR(50) NOT NULL,
                          last_name VARCHAR(50) NOT NULL,
                          username VARCHAR(50) UNIQUE NOT NULL,
                          email VARCHAR(100) UNIQUE NOT NULL,
                          password_hash VARCHAR(255) NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                          order_id INT AUTO_INCREMENT PRIMARY KEY,
                          customer_name VARCHAR(100),
                          phone_number VARCHAR(15),
                          customer_address TEXT,
                          total_price DECIMAL(10,2),
                          order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                          user_id INT,
                          FOREIGN KEY (user_id) REFERENCES users(id))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
                          id INT AUTO_INCREMENT PRIMARY KEY,
                          order_id INT,
                          item_name VARCHAR(50),
                          quantity INT,
                          item_total DECIMAL(10,2),
                          FOREIGN KEY (order_id) REFERENCES orders(order_id))''')
        conn.commit()
        logger.info("Tables created or verified successfully.")
        return True
    except mysql.connector.Error as err:
        logger.error(f"Error creating tables: {err}")
        return False
    finally:
        cursor.close()
        conn.close()

def save_user(first_name, last_name, username, email, password):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        password_hash = generate_password_hash(password)
        cursor.execute('''INSERT INTO users (first_name, last_name, username, email, password_hash)
                          VALUES (%s, %s, %s, %s, %s)''', 
                       (first_name, last_name, username, email, password_hash))
        conn.commit()
        return cursor.lastrowid
    except mysql.connector.Error as err:
        logger.error(f"Error saving user: {err}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def get_user(username):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        return cursor.fetchone()
    except mysql.connector.Error as err:
        logger.error(f"Error fetching user: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

def save_order_to_db(customer_name, phone_number, customer_address, order_details, total_price, user_id):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute('''INSERT INTO orders (customer_name, phone_number, customer_address, total_price, user_id)
                          VALUES (%s, %s, %s, %s, %s)''', 
                       (customer_name, phone_number, customer_address, total_price, user_id))
        order_id = cursor.lastrowid
        for item, details in order_details.items():
            cursor.execute('''INSERT INTO order_items (order_id, item_name, quantity, item_total)
                              VALUES (%s, %s, %s, %s)''', 
                           (order_id, item, details['quantity'], details['item_total']))
        conn.commit()
        logger.info(f"Order {order_id} saved successfully.")
        return order_id
    except mysql.connector.Error as err:
        conn.rollback()
        logger.error(f"Error saving order: {err}")
        return None
    finally:
        cursor.close()
        conn.close()

create_tables()