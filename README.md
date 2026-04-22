# 🌿 CHUK WhatsApp Chatbot
### by Pakka Ltd

A fully automated WhatsApp Business chatbot built for CHUK — India's premium eco-friendly tableware brand. The chatbot handles customer registration, product browsing, order placement, order tracking, distributor onboarding, and customer support — all through WhatsApp.

---

## 🆕 Recent Updates (April 2024)
- **Windows Stability Fix**: Removed all emoji print statements from the console output to prevent `UnicodeEncodeError` on Windows machines.
- **Security Enhancement**: Updated Twilio webhook validation and input sanitization.
- **Environment Setup**: Added `.env.example` for easier local configuration.

---

## 📱 Features

| Feature | Description |
|---------|-------------|
| 👤 User Registration | OTP-based WhatsApp registration with customer ID generation |
| 🛍️ Product Catalog | Browse products by category with pricing details |
| 🛒 Order Placement | Place orders with delivery location and business details |
| 🚚 Order Tracking | Track orders by Order ID or mobile number |
| 🤝 Distributor Onboarding | Apply to become a CHUK distributor |
| 📞 Customer Support | Raise support tickets with auto Ticket ID generation |
| 🔐 Security | Rate limiting, input sanitization, SQL injection prevention |
| ☁️ Deployment | Live 24/7 on Railway.app — completely free |

---

## 🏗️ System Architecture

```
User (WhatsApp)
      ↓
WhatsApp Business API
      ↓
Twilio (Messaging Gateway)
      ↓
Webhook (Flask API)
      ↓
Backend Server (Python + Flask)
      ↓
MySQL Database
      ↓
Reply → User
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|-----------|---------|
| Python 3 | Programming Language |
| Flask | Web Framework / Backend Server |
| MySQL | Relational Database |
| Twilio | WhatsApp Business API |
| Railway.app | Cloud Hosting (Free) |
| GitHub | Version Control |
| Gunicorn | Production WSGI Server |
| ngrok | Local Development Tunnel |

---

## 📁 Project Structure

```
chuk_bot/
├── app.py                  # Main Flask server with webhook
├── db.py                   # MySQL database connection
├── security.py             # Rate limiting & input sanitization
├── error_handler.py        # Global error handling & logging
├── requirements.txt        # Python dependencies
├── Procfile                # Railway deployment config
├── .gitignore              # Git ignore rules
├── database_setup.sql      # Database schema & sample data
├── setup.py                # Auto file creator script
└── chatbot/
    ├── __init__.py
    ├── handler.py          # Main chatbot brain & message router
    ├── session_manager.py  # Conversation state management
    ├── auth.py             # User registration & OTP verification
    ├── products.py         # Product catalog & display
    ├── orders.py           # Order placement & tracking
    ├── support.py          # Customer support tickets
    └── distributor.py      # Distributor registration
```

---

## 🗄️ Database Schema

```
chuk_bot/
├── users                   # Customer profiles & authentication
├── products                # Product catalog (8 items, 5 categories)
├── orders                  # Placed orders with status tracking
├── tickets                 # Customer support tickets
├── sessions                # Conversation state per user
└── distributor_requests    # Distributor applications
```

---

## 🚀 Local Setup Guide

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- Twilio Account
- ngrok

### Step 1 — Clone Repository
```bash
git clone https://github.com/ashhabakhtar/chuk_bot.git
cd chuk_bot
```

### Step 2 — Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Configure Environment
Create `.env` file:
```env
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=chuk_bot
FLASK_SECRET_KEY=chuk_super_secret_key_2024
FLASK_PORT=5000
```

### Step 4 — Setup Database
```bash
# Open MySQL Workbench and run:
database_setup.sql
```

### Step 5 — Run Server
```bash
python app.py
```

### Step 6 — Start ngrok Tunnel
```bash
ngrok http 5000
```

### Step 7 — Configure Twilio Webhook
```
twilio.com → Messaging → Try it out
→ Send a WhatsApp message
→ Sandbox Settings
→ Paste: https://xxxx.ngrok-free.app/webhook
→ HTTP POST → Save
```

---

## ☁️ Railway Deployment

### Step 1 — Push to GitHub
```bash
git add .
git commit -m "Deploy CHUK chatbot"
git push origin main
```

### Step 2 — Deploy on Railway
```
1. railway.app → Login with GitHub
2. New Project → Deploy from GitHub
3. Select chuk_bot repository
4. Add MySQL database
5. Add environment variables
6. Generate public domain
7. Update Twilio webhook URL
```

### Step 3 — Setup Database on Railway
```
Open browser:
https://your-app.up.railway.app/setup-db
```

---

## 💬 Chatbot Flow

```
User sends "Hi"
      ↓
New User?
├── YES → Registration Flow
│         Name → Email → Type → OTP → Verified
└── NO  → Main Menu

Main Menu:
1️⃣ View Products  → Browse Categories → Products
2️⃣ Place Order    → Select Product → Qty → Location → Confirm
3️⃣ Track Order    → Enter Order ID → Status
4️⃣ Distributor    → Business Details → Submit
5️⃣ Support        → Issue Type → Description → Ticket ID
```

---

## 🔐 Security Features

- ✅ Rate limiting (20 messages/minute per user)
- ✅ Input sanitization (SQL injection prevention)
- ✅ Parameterized database queries
- ✅ Environment variables for secrets
- ✅ Error logging to errors.log
- ✅ Friendly error messages (app never crashes)

---

## 📊 ID Formats

| Type | Format | Example |
|------|--------|---------|
| Customer ID | CHUK-XXXXX | CHUK-00001 |
| Order ID | PK-XXXXX | PK-00001 |
| Ticket ID | PK-TXXXX | PK-T0001 |

---

## 🧪 Testing Checklist

| Test | Description |
|------|-------------|
| Registration | New user registration with OTP |
| Login | Returning user recognition |
| Products | Browse all 5 categories |
| Order | Place order end to end |
| Tracking | Track by Order ID and mobile |
| Support | Create support ticket |
| Distributor | Submit distributor request |
| Security | Rate limit and sanitization |

---

## 📦 Product Categories

- 🍽️ Plates (Round — Large, Medium, Small)
- 🥣 Bowls (Deep Bowl, Curry Bowl)
- 🫙 Trays (Serving Tray)
- 📦 Containers (Food Container)
- 🥄 Utensils (Spoon Set)

---

## 👨‍💻 Developer

**Ashhab Akhtar**
GitHub: [@ashhabakhtar](https://github.com/ashhabakhtar)

---

## 🏢 About CHUK

CHUK is India's leading eco-friendly tableware brand by Pakka Ltd. Products are made from sustainable materials and are 100% biodegradable — perfect for food service businesses looking to go green.

---

## 📄 License

This project is built for Pakka Ltd / CHUK brand.
All rights reserved © 2024 Pakka Ltd.

---

## 🔜 Roadmap

- [ ] Real Twilio WhatsApp Business number
- [ ] Admin dashboard for order management
- [ ] Payment gateway integration
- [ ] Multi-language support (Hindi)
- [ ] Analytics and reporting
- [ ] Automated order status updates