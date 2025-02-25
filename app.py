from flask import Flask, render_template, redirect, url_for, flash, request, session
import logging
import json
from database import save_order_to_db, get_db_connection
from dotenv import load_dotenv
import os
from auth import auth_bp
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

app.register_blueprint(auth_bp, url_prefix='/auth')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ITEM_PRICES = {
    "Pasta": 120.00,
    "Chi-Momo": 160.00,
    "Burger": 220.00,
    "Coffee": 120.00,
    "Tea": 30.00,
    "Chowmein": 180.00,
    "Samosa": 35.00,
    "Keema Noodles": 190.00,
    "Laphing": 120.00,
    "Corn Dog": 220.00,
    "Sauces": 330.00,
    "Momo": 150.00
}

def format_currency(value):
    return f"Nrs: {value:,.2f}"

@app.template_filter('format_currency')
def format_currency_filter(value):
    return format_currency(value)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in to access this page.", "error")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    user = None
    user_id = session.get('user_id')
    if user_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()
        except Exception as e:
            logger.error(f"Error fetching user from DB: {e}", exc_info=True)
    return dict(user=user)

@app.route('/')
@app.route('/index.html')
def index():
    return render_template('index.html')

@app.route('/contactus.html')
def contactUs():
    return render_template('contactus.html')

@app.route('/aboutus.html')
def aboutus():
    return render_template('aboutus.html')

@app.route('/viewMenu.html', methods=['GET', 'POST'])
@login_required  # Added login requirement
def view_menu():
    if request.method == 'POST':
        items = {}
        for item in ITEM_PRICES:
            qty = request.form.get(item, 0)
            try:
                qty = int(qty)
                if qty > 0:
                    items[item] = qty
            except ValueError:
                flash(f"Invalid quantity for {item}.", "error")
                return redirect(url_for('view_menu'))
        if not items:
            flash("Please select at least one item!", "error")
            return redirect(url_for('view_menu'))
        total_price = sum(ITEM_PRICES[item] * qty for item, qty in items.items())
        return render_template('order.html', items=items, total_price=total_price, ITEM_PRICES=ITEM_PRICES)
    return render_template('viewMenu.html')

@app.route('/order.html', methods=['GET', 'POST'])
@login_required
def order():
    if request.method == 'POST':
        customer_name = request.form.get('customer-name', '').strip()
        phone_number = request.form.get('phone-number', '').strip()
        customer_address = request.form.get('customer-address', '').strip()
        house_no = request.form.get('house-no', '').strip()
        items_raw = request.form.get('items', '').strip()
        user_id = session.get('user_id')

        if not all([customer_name, phone_number, customer_address, items_raw]):
            flash("Please fill in all required fields.", "error")
            return redirect(url_for('view_menu'))

        try:
            items = json.loads(items_raw)
            if not isinstance(items, dict):
                raise ValueError("Invalid items format")
            order_details = {}
            total_price = 0
            for item_name, quantity in items.items():
                quantity = int(quantity)
                if quantity <= 0:
                    continue
                if item_name not in ITEM_PRICES:
                    flash(f"Item '{item_name}' is not available.", "error")
                    return redirect(url_for('view_menu'))
                item_price = ITEM_PRICES[item_name]
                item_total = item_price * quantity
                order_details[item_name] = {'quantity': quantity, 'item_total': item_total}
                total_price += item_total
        except json.JSONDecodeError as e:
            flash("Invalid item data format. Please try again.", "error")
            logger.error(f"JSON decode error: {e}")
            return redirect(url_for('view_menu'))
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for('view_menu'))

        try:
            order_id = save_order_to_db(customer_name, phone_number, customer_address, order_details, total_price, user_id)
            if not order_id:
                flash("Failed to save order. Please try again.", "error")
                return redirect(url_for('view_menu'))
        except Exception as e:
            flash("An error occurred while saving your order. Please try again.", "error")
            logger.error(f"Database save error: {e}", exc_info=True)
            return redirect(url_for('view_menu'))

        return render_template('order_summary.html',
                               customer_name=customer_name,
                               customer_address=customer_address,
                               house_no=house_no if house_no else 'N/A',
                               phone_number=phone_number,
                               order_details=order_details,
                               total_price=total_price)
    
    return redirect(url_for('view_menu'))

if __name__ == '__main__':
    app.run(debug=True)