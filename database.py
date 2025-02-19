import mysql.connector
import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Define MySQL connection parameters using environment variables
DB_CONFIG = {
    "host": os.getenv('DB_HOST', 'localhost'),
    "user": os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD', ''),
    "database": os.getenv('DB_NAME', 'gourmetBistro_db')
}

# Utility function to connect to the database
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        return None

# Function to create the required tables in the database
def create_tables(cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
                        order_id INT AUTO_INCREMENT PRIMARY KEY,
                        customer_name VARCHAR(255),
                        phone_number VARCHAR(25),
                        order_date DATETIME,
                        total_price DECIMAL(10,2))''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS order_items (
                        item_id INT AUTO_INCREMENT PRIMARY KEY,
                        order_id INT,
                        item_name VARCHAR(255),
                        quantity INT,
                        item_total DECIMAL(10,2),
                        FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE)''')

# Function to insert the order into the database
def save_order_to_db(customer_name, phone_number, total_price, order_details):
    conn = get_db_connection()
    if not conn:
        return None

    cursor = conn.cursor()
    try:
        create_tables(cursor)

        # Insert the order
        cursor.execute('''INSERT INTO orders (customer_name, phone_number, order_date, total_price)
                        VALUES (%s, %s, NOW(), %s)''', (customer_name, phone_number, total_price))

        order_id = cursor.lastrowid  # Get the last inserted order ID

        # Insert the order items
        for item, details in order_details.items():
            cursor.execute('''INSERT INTO order_items (order_id, item_name, quantity, item_total)
                            VALUES (%s, %s, %s, %s)''', (order_id, item, details["quantity"], details["item_total"]))

        conn.commit()
        return order_id
    except mysql.connector.Error as err:
        conn.rollback()
        logger.error(f"Database error: {err}")
        return None
    finally:
        cursor.close()
        conn.close()
