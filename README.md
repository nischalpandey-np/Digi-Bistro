# 🍽️ Digi Bistro

Digi Bistro is a web-based prototype restaurant ordering system where users can browse the menu, place orders, and register/login to track their orders which will be safely stored in database.

---

## 📂 Project Structure
```
Digi-Bistro/
├── static/               # Static files (CSS, JS, Images)
│   ├── styles.css        # Stylesheet for the website
│   ├── script.js         # JavaScript for frontend functionality
│   ├── hero.jpg          # Hero image
│   ├── pasta.jpg         # Menu item images
│   ├── chi-momo.jpg
│   ├── momo.jpg
│   ├── burger.jpg
│   ├── coffee.jpg
│   ├── tea.jpg
│   ├── chowmein.jpg
│   └── samosa.jpg
├── templates/            # HTML Templates
│   ├── index.html        # Homepage
│   ├── viewMenu.html     # Menu page
│   ├── order.html        # Order placement page
│   ├── order_summary.html # Order summary
│   ├── login.html        # User login page
│   └── register.html     # User registration page
├── app.py                # Main Flask application
├── auth.py               # User authentication logic
├── database.py           # Database connection & models
└── .env                  # Environment variables (DO NOT SHARE)
```

---

## 🚀 Features
- 🍽️ **View Menu** - Browse restaurant menu with images
- 🛒 **Order System** - Place orders online
- 🔐 **User Authentication** - Register/Login system
- 📦 **Order Tracking** - View past orders
- 💳 **Payment Integration** (Planning) - coming soon

---

## 🛠️ Setup & Installation
### 1️⃣ Clone the Repository
```sh
git clone https://github.com/YOUR_USERNAME/Digi-Bistro.git
cd Digi-Bistro
```

### 2️⃣ Create a Virtual Environment
```sh
python -m venv venv
source venv/bin/activate   # On Windows use: venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables
Create a `.env` file and add:
```
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
```

### 5️⃣ Run the Application
```sh
python app.py
```
Go to `http://127.0.0.1:5000/` in your browser.

---

## 📜 License
This project is licensed under the MIT License.

---

## 🤝 Contributing
Feel free to fork and contribute! Pull requests are welcome.

---

## 📞 Contact
- **Developer:** Nischal Pandey
- **Email:** nischalpandey0204@gmail.com
- **GitHub:** [Your GitHub](https://github.com/nischalpandey-np)

---

🌟 **If you like this project, give it a star on GitHub!** 🌟

