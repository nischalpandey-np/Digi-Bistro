from flask import Flask, render_template, request, redirect, url_for, flash
import datetime
import mysql.connector
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Required for flash messages and CSRF protection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define MySQL connection parameters using environment variables
DB_CONFIG = {
    "host": os.getenv('DB_HOST', 'localhost'),
    "user": os.getenv('DB_USER', 'root'),
    "password": os.getenv('DB_PASSWORD', ''),
    "database": os.getenv('DB_NAME', 'gourmetBistro_db')
}

# Define item prices
ITEM_PRICES = {
    "Pasta": 120.00,
    "Momo": 160.00,
    "Burger": 220.00,
    "Coffee": 130.00,
    "Tea": 30.00,
    "Chowmein": 175.00,
    "Samosa": 35.00
}

# Utility function to format currency
def format_currency(value):
    return f"Nrs: {value:,.2f}"

@app.template_filter('format_currency')
def format_currency_filter(value):
    return format_currency(value)

# Utility function to connect to the database
def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        logger.error(f"Database connection error: {err}")
        flash("Database connection error. Please try again later.", "error")
        return None

@app.route('/')
def index():
    return render_template('index1.html')

@app.route('/viewMenu.html')
def view_menu():
    return render_template('viewMenu.html')

@app.route('/order.html', methods=['GET', 'POST'])
def order():
    if request.method == 'POST':
        # Get and validate form data
        customer_name = request.form.get('customer-name', '').strip()
        phone_number = request.form.get('phone-number', '').strip()
        items_raw = request.form.get('items', '').strip()

        if not customer_name  or not phone_number or not items_raw:
            flash("All fields are required. Please fill out the form completely.", "error")
            return redirect(url_for('order'))

        try:
            phone_number = int(phone_number)
        except ValueError:
            flash("Invalid phone number. Please enter a valid number.", "error")
            return redirect(url_for('order'))

        # Parse items and calculate total price
        order_details = {}
        total_price = 0

        try:
            items = items_raw.split(',')
            for item in items:
                item_parts = item.split('=')
                if len(item_parts) != 2:
                    flash(f"Error: Incorrect item format in '{item}'.", "error")
                    return redirect(url_for('order'))

                item_name, quantity_str = item_parts
                item_name = item_name.strip()

                try:
                    quantity = int(quantity_str.strip())
                    if quantity <= 0:
                        continue  # Skip items with zero or negative quantity

                    if item_name in ITEM_PRICES:
                        item_total = ITEM_PRICES[item_name] * quantity
                        total_price += item_total
                        order_details[item_name] = {
                            'quantity': quantity,
                            'item_total': item_total
                        }
                    else:
                        flash(f"Error: Item '{item_name}' not found in menu.", "error")
                        return redirect(url_for('order'))
                except ValueError:
                    flash(f"Error: Quantity '{quantity_str}' is not a valid number.", "error")
                    return redirect(url_for('order'))
        except Exception as e:
            logger.error(f"Error processing order: {e}")
            flash("An error occurred while processing your order. Please try again.", "error")
            return redirect(url_for('order'))

        # Save order to the database
        conn = get_db_connection()
        if not conn:
            return redirect(url_for('order'))

        cursor = conn.cursor()
        try:
            # Create tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INT AUTO_INCREMENT PRIMARY KEY,
                    customer_name VARCHAR(255),
                    phone_number VARCHAR(15),
                    order_date DATETIME,
                    total_price DECIMAL(10,2)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    item_id INT AUTO_INCREMENT PRIMARY KEY,
                    order_id INT,
                    item_name VARCHAR(255),
                    quantity INT,
                    item_total DECIMAL(10,2),
                    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
                )
            ''')

            # Insert order into `orders` table
            order_date = datetime.datetime.now()
            cursor.execute('''
                INSERT INTO orders (customer_name,  phone_number, order_date, total_price)
                VALUES (%s, %s, %s, %s)
            ''', (customer_name, phone_number, order_date, total_price))

            order_id = cursor.lastrowid  # Get the last inserted order ID

            # Insert items into `order_items` table
            for item, details in order_details.items():
                cursor.execute('''
                    INSERT INTO order_items (order_id, item_name, quantity, item_total)
                    VALUES (%s, %s, %s, %s)
                ''', (order_id, item, details["quantity"], details["item_total"]))

            # Commit changes
            conn.commit()
            logger.info(f"Order saved successfully for customer: {customer_name}")
            flash("Your order has been placed successfully!", "success")

        except mysql.connector.Error as err:
            logger.error(f"Database error: {err}")
            conn.rollback()
            flash("An error occurred while saving your order. Please try again.", "error")
        finally:
            cursor.close()
            conn.close()

        return render_template('order_summary.html',
                              customer_name=customer_name,
                              phone_number=phone_number,
                              order_details=order_details,
                              total_price=total_price,
                              format_currency=format_currency)

    return render_template('order.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')