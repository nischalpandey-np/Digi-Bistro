from flask import Flask, render_template, request, redirect, url_for, flash
import logging
from database import save_order_to_db
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')  # Required for flash messages and CSRF protection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        order_id = save_order_to_db(customer_name, phone_number, total_price, order_details)
        if not order_id:
            flash("An error occurred while saving your order. Please try again.", "error")
            return redirect(url_for('order'))

        logger.info(f"Order saved successfully for customer: {customer_name}")
        flash("Your order has been placed successfully!", "success")

        return render_template('order_summary.html',
                              customer_name=customer_name,
                              phone_number=phone_number,
                              order_details=order_details,
                              total_price=total_price,
                              format_currency=format_currency)

    return render_template('order.html')

if __name__ == '__main__':
    app.run(debug=False)
