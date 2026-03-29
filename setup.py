import os

# Create chatbot directory
os.makedirs("chatbot", exist_ok=True)

files = {}

files["chatbot/__init__.py"] = ""

files["chatbot/session_manager.py"] = '''from db import execute_query
import json

def get_session(mobile):
    rows = execute_query(
        "SELECT current_step, temp_data FROM sessions WHERE mobile = %s",
        (mobile,), fetch=True
    )
    if rows:
        temp = rows[0]["temp_data"]
        return {"current_step": rows[0]["current_step"], "temp_data": json.loads(temp) if temp else {}}
    else:
        execute_query(
            "INSERT INTO sessions (mobile, current_step, temp_data) VALUES (%s, %s, %s)",
            (mobile, "new_user", "{}")
        )
        return {"current_step": "new_user", "temp_data": {}}

def update_session(mobile, step, temp_data=None):
    execute_query(
        "UPDATE sessions SET current_step = %s, temp_data = %s WHERE mobile = %s",
        (step, json.dumps(temp_data or {}), mobile)
    )

def clear_session(mobile):
    execute_query(
        "UPDATE sessions SET current_step = %s, temp_data = %s WHERE mobile = %s",
        ("main_menu", "{}", mobile)
    )
'''

files["chatbot/auth.py"] = '''from db import execute_query
from dotenv import load_dotenv
import os, random, requests
load_dotenv()

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(mobile, otp):
    try:
        from twilio.rest import Client
        client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
        clean = mobile.replace("whatsapp:", "")
        client.messages.create(
            body=f"Your CHUK verification code is: {otp}. Valid for 5 minutes.",
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            to=f"whatsapp:{clean}"
        )
        return True
    except Exception as e:
        print(f"OTP send failed: {e}")
        return False

def user_exists(mobile):
    rows = execute_query("SELECT customer_id FROM users WHERE mobile = %s", (mobile,), fetch=True)
    return len(rows) > 0 if rows else False

def get_user(mobile):
    rows = execute_query("SELECT * FROM users WHERE mobile = %s", (mobile,), fetch=True)
    return rows[0] if rows else None

def generate_customer_id():
    rows = execute_query("SELECT COUNT(*) as total FROM users", fetch=True)
    count = rows[0]["total"] + 1 if rows else 1
    return f"CHUK-{str(count).zfill(5)}"

def register_user(name, email, mobile, customer_type):
    customer_id = generate_customer_id()
    otp = generate_otp()
    execute_query(
        "INSERT INTO users (customer_id, name, email, mobile, customer_type, otp, is_verified) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (customer_id, name, email, mobile, customer_type, otp, False)
    )
    send_otp(mobile, otp)
    return customer_id, otp

def verify_otp(mobile, entered_otp):
    rows = execute_query("SELECT otp FROM users WHERE mobile = %s", (mobile,), fetch=True)
    if rows and rows[0]["otp"] == entered_otp:
        execute_query("UPDATE users SET is_verified = TRUE, otp = NULL WHERE mobile = %s", (mobile,))
        return True
    return False
'''

files["chatbot/products.py"] = '''from db import execute_query

def get_categories():
    rows = execute_query("SELECT DISTINCT category FROM products WHERE stock_available = TRUE", fetch=True)
    return [row["category"] for row in rows] if rows else []

def get_products_by_category(category):
    rows = execute_query("SELECT * FROM products WHERE category = %s AND stock_available = TRUE", (category,), fetch=True)
    return rows if rows else []

def get_product_by_id(product_id):
    rows = execute_query("SELECT * FROM products WHERE product_id = %s", (product_id,), fetch=True)
    return rows[0] if rows else None

def format_categories_message():
    categories = get_categories()
    if not categories:
        return "No products available right now."
    msg = "*CHUK Product Categories*\n\n"
    for i, cat in enumerate(categories, 1):
        msg += f"{i}. {cat}\n"
    msg += "\nReply with the number to browse.\n0 = Main Menu"
    return msg

def format_products_message(category):
    products = get_products_by_category(category)
    if not products:
        return f"No products found in {category}."
    msg = f"*{category} Products*\n\n"
    for p in products:
        msg += f"*{p[\'name\']}*\n"
        msg += f"Size: {p[\'size\']} | Weight: {p[\'weight_grams\']}g\n"
        msg += f"Pack of: {p[\'packaging_qty\']} | Price: Rs.{p[\'price_per_pack\']}\n"
        msg += f"ID: #{p[\'product_id\']}\n\n"
    msg += "Reply with product ID to order.\n0 = Back"
    return msg
'''

files["chatbot/orders.py"] = '''from db import execute_query

def generate_order_id():
    rows = execute_query("SELECT COUNT(*) as total FROM orders", fetch=True)
    count = rows[0]["total"] + 1 if rows else 1
    return f"PK-{str(count).zfill(5)}"

def place_order(customer_id, product_id, quantity, delivery_location, business_name):
    order_id = generate_order_id()
    execute_query(
        "INSERT INTO orders (order_id, customer_id, product_id, quantity, delivery_location, business_name, status) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (order_id, customer_id, product_id, quantity, delivery_location, business_name, "processing")
    )
    return order_id

def track_by_order_id(order_id):
    rows = execute_query(
        "SELECT o.*, p.name as product_name FROM orders o JOIN products p ON o.product_id = p.product_id WHERE o.order_id = %s",
        (order_id,), fetch=True
    )
    return rows[0] if rows else None

def track_by_mobile(mobile):
    rows = execute_query(
        "SELECT o.*, p.name as product_name FROM orders o JOIN products p ON o.product_id = p.product_id JOIN users u ON o.customer_id = u.customer_id WHERE u.mobile = %s ORDER BY o.created_at DESC LIMIT 5",
        (mobile,), fetch=True
    )
    return rows if rows else []

def format_order_confirmation(order_id, product_name, quantity, location):
    msg  = "*Order Placed Successfully!*\n\n"
    msg += f"Order ID: *{order_id}*\n"
    msg += f"Product: {product_name}\n"
    msg += f"Quantity: {quantity} packs\n"
    msg += f"Delivery: {location}\n"
    msg += f"Status: Processing\n\n"
    msg += "Our sales team will contact you shortly."
    return msg

def format_tracking_message(order):
    emoji = {"processing":"Processing","confirmed":"Confirmed","dispatched":"Dispatched","delivered":"Delivered","cancelled":"Cancelled"}
    msg  = "*Order Tracking*\n\n"
    msg += f"Order ID: *{order[\'order_id\']}*\n"
    msg += f"Product: {order[\'product_name\']}\n"
    msg += f"Quantity: {order[\'quantity\']} packs\n"
    msg += f"Location: {order[\'delivery_location\']}\n"
    msg += f"Status: *{emoji.get(order[\'status\'], order[\'status\'])}*"
    return msg
'''

files["chatbot/support.py"] = '''from db import execute_query

def generate_ticket_id():
    rows = execute_query("SELECT COUNT(*) as total FROM tickets", fetch=True)
    count = rows[0]["total"] + 1 if rows else 1
    return f"PK-T{str(count).zfill(4)}"

def create_ticket(customer_id, issue_type, description):
    ticket_id = generate_ticket_id()
    execute_query(
        "INSERT INTO tickets (ticket_id, customer_id, issue_type, description, status) VALUES (%s,%s,%s,%s,%s)",
        (ticket_id, customer_id, issue_type, description, "open")
    )
    return ticket_id

def format_ticket_confirmation(ticket_id, issue_type):
    msg  = "*Support Ticket Created!*\n\n"
    msg += f"Ticket ID: *{ticket_id}*\n"
    msg += f"Issue: {issue_type.replace(\'_\', \' \').title()}\n"
    msg += "Status: Open\n\n"
    msg += "Our team will contact you within 24 hours."
    return msg
'''

files["chatbot/distributor.py"] = '''from db import execute_query

def save_distributor_request(business_name, location, experience, mobile, email=""):
    execute_query(
        "INSERT INTO distributor_requests (business_name, location, experience_years, contact_mobile, contact_email, status) VALUES (%s,%s,%s,%s,%s,%s)",
        (business_name, location, experience, mobile, email, "pending")
    )

def format_distributor_confirmation(business_name):
    msg  = "*Distributor Request Submitted!*\n\n"
    msg += f"Business: {business_name}\n"
    msg += "Status: Under Review\n\n"
    msg += "Our sales team will contact you within 2-3 business days."
    return msg
'''

files["chatbot/handler.py"] = '''from chatbot.session_manager import get_session, update_session, clear_session
from chatbot.auth import user_exists, get_user, register_user, verify_otp
from chatbot.products import get_categories, get_product_by_id, format_categories_message, format_products_message
from chatbot.orders import place_order, track_by_order_id, track_by_mobile, format_order_confirmation, format_tracking_message
from chatbot.support import create_ticket, format_ticket_confirmation
from chatbot.distributor import save_distributor_request, format_distributor_confirmation

def handle_message(sender, message):
    mobile = sender.replace("whatsapp:", "")
    session = get_session(mobile)
    step = session["current_step"]
    temp = session["temp_data"]
    msg = message.strip().lower()

    if msg in ["hi", "hello", "hey", "start", "menu", "0"]:
        return handle_start(mobile)
    if msg == "cancel":
        clear_session(mobile)
        return "Cancelled.\n\n" + get_main_menu()

    if step == "new_user": return handle_start(mobile)
    elif step == "awaiting_name": return reg_name(mobile, message, temp)
    elif step == "awaiting_email": return reg_email(mobile, message, temp)
    elif step == "awaiting_customer_type": return reg_type(mobile, message, temp)
    elif step == "awaiting_otp": return reg_otp(mobile, message, temp)
    elif step == "main_menu": return main_menu(mobile, msg, temp)
    elif step == "browsing_categories": return cat_select(mobile, msg)
    elif step == "browsing_products": return prod_select(mobile, msg, temp)
    elif step == "awaiting_order_quantity": return ord_qty(mobile, message, temp)
    elif step == "awaiting_delivery_location": return ord_loc(mobile, message, temp)
    elif step == "awaiting_business_name": return ord_biz(mobile, message, temp)
    elif step == "confirm_order": return ord_confirm(mobile, msg, temp)
    elif step == "awaiting_tracking_input": return tracking(mobile, message)
    elif step == "awaiting_issue_type": return sup_issue(mobile, msg, temp)
    elif step == "awaiting_issue_description": return sup_desc(mobile, message, temp)
    elif step == "awaiting_biz_name": return dist_name(mobile, message, temp)
    elif step == "awaiting_biz_location": return dist_loc(mobile, message, temp)
    elif step == "awaiting_biz_experience": return dist_exp(mobile, message, temp)
    else:
        clear_session(mobile)
        return "Session reset.\n\n" + get_main_menu()

def handle_start(mobile):
    if user_exists(mobile):
        user = get_user(mobile)
        update_session(mobile, "main_menu")
        return f"Welcome back, *{user[\'name\']}*!\nID: {user[\'customer_id\']}\n\n" + get_main_menu()
    update_session(mobile, "awaiting_name")
    return "Welcome to *CHUK by Pakka Ltd*!\n\nEnter your *Full Name*:"

def get_main_menu():
    return "*Main Menu*\n1 - View Products\n2 - Place Order\n3 - Track Order\n4 - Become Distributor\n5 - Customer Support\n\nReply 1-5"

def main_menu(mobile, msg, temp):
    if msg == "1":
        update_session(mobile, "browsing_categories")
        return format_categories_message()
    elif msg == "2":
        update_session(mobile, "browsing_categories", {"ordering": True})
        return format_categories_message()
    elif msg == "3":
        update_session(mobile, "awaiting_tracking_input")
        return "Enter Order ID (PK-XXXXX) or mobile number:"
    elif msg == "4":
        update_session(mobile, "awaiting_biz_name")
        return "Enter your *Business Name*:"
    elif msg == "5":
        update_session(mobile, "awaiting_issue_type")
        return "Support:\n1 - Damaged Product\n2 - Order Issue\n3 - General Inquiry\n4 - Talk to Agent\n\nReply 1-4"
    return "Invalid option.\n\n" + get_main_menu()

def reg_name(mobile, message, temp):
    if len(message.strip()) < 2:
        return "Name too short. Enter full name:"
    temp["name"] = message.strip()
    update_session(mobile, "awaiting_email", temp)
    return f"Name: *{temp[\'name\']}*\n\nEnter *Email Address*:"

def reg_email(mobile, message, temp):
    if "@" not in message or "." not in message:
        return "Invalid email. Try again:"
    temp["email"] = message.strip().lower()
    update_session(mobile, "awaiting_customer_type", temp)
    return "Select *Customer Type*:\n1 - Retailer\n2 - Wholesaler\n3 - Individual"

def reg_type(mobile, message, temp):
    types = {"1": "retailer", "2": "wholesaler", "3": "individual"}
    if message.strip() not in types:
        return "Reply 1, 2, or 3:"
    temp["customer_type"] = types[message.strip()]
    customer_id, otp = register_user(temp["name"], temp["email"], mobile, temp["customer_type"])
    temp["customer_id"] = customer_id
    update_session(mobile, "awaiting_otp", temp)
    return f"OTP sent to *{mobile}*\n\nEnter the *6-digit OTP*:"

def reg_otp(mobile, message, temp):
    if verify_otp(mobile, message.strip()):
        update_session(mobile, "main_menu")
        return f"*Registration Successful!*\nID: *{temp.get(\'customer_id\')}*\n\nWelcome to CHUK!\n\n" + get_main_menu()
    return "Invalid OTP. Try again:"

def cat_select(mobile, msg):
    if msg == "0":
        update_session(mobile, "main_menu")
        return get_main_menu()
    categories = get_categories()
    try:
        index = int(msg) - 1
        if 0 <= index < len(categories):
            selected = categories[index]
            session = get_session(mobile)
            temp = session["temp_data"]
            temp["selected_category"] = selected
            update_session(mobile, "browsing_products", temp)
            return format_products_message(selected)
        return "Invalid option.\n\n" + format_categories_message()
    except ValueError:
        return "Reply with a number."

def prod_select(mobile, msg, temp):
    if msg == "0":
        update_session(mobile, "browsing_categories", temp)
        return format_categories_message()
    try:
        product = get_product_by_id(int(msg))
        if product:
            temp["product_id"] = product["product_id"]
            temp["product_name"] = product["name"]
            update_session(mobile, "awaiting_order_quantity", temp)
            return f"Selected: *{product[\'name\']}*\nPrice: Rs.{product[\'price_per_pack\']} per pack\n\nEnter *Quantity* (packs):"
        return "Product not found. Enter valid ID."
    except ValueError:
        return "Enter product ID number."

def ord_qty(mobile, message, temp):
    try:
        qty = int(message.strip())
        if qty <= 0:
            return "Quantity must be at least 1:"
        temp["quantity"] = qty
        update_session(mobile, "awaiting_delivery_location", temp)
        return "Enter *Delivery Address*:"
    except ValueError:
        return "Enter a valid number:"

def ord_loc(mobile, message, temp):
    if len(message.strip()) < 5:
        return "Enter complete address:"
    temp["delivery_location"] = message.strip()
    update_session(mobile, "awaiting_business_name", temp)
    return "Enter *Business Name* (or type NA):"

def ord_biz(mobile, message, temp):
    temp["business_name"] = message.strip()
    update_session(mobile, "confirm_order", temp)
    product = get_product_by_id(temp["product_id"])
    total = product["price_per_pack"] * temp["quantity"]
    return f"*Order Summary*\nProduct: {temp[\'product_name\']}\nQty: {temp[\'quantity\']} packs\nTotal: Rs.{total}\nDelivery: {temp[\'delivery_location\']}\nBusiness: {temp[\'business_name\']}\n\nReply *YES* to confirm or *NO* to cancel"

def ord_confirm(mobile, msg, temp):
    if msg == "yes":
        user = get_user(mobile)
        order_id = place_order(user["customer_id"], temp["product_id"], temp["quantity"], temp["delivery_location"], temp["business_name"])
        clear_session(mobile)
        return format_order_confirmation(order_id, temp["product_name"], temp["quantity"], temp["delivery_location"]) + "\n\n" + get_main_menu()
    elif msg == "no":
        clear_session(mobile)
        return "Order cancelled.\n\n" + get_main_menu()
    return "Reply YES or NO."

def tracking(mobile, message):
    query = message.strip()
    if query.upper().startswith("PK-"):
        order = track_by_order_id(query.upper())
        if order:
            clear_session(mobile)
            return format_tracking_message(order) + "\n\n" + get_main_menu()
        return "No order found with that ID."
    orders = track_by_mobile(query)
    if orders:
        clear_session(mobile)
        reply = "Your Recent Orders:\n\n"
        for o in orders:
            reply += format_tracking_message(o) + "\n---\n"
        return reply + "\n" + get_main_menu()
    return "No orders found. Try your Order ID (PK-XXXXX)"

def sup_issue(mobile, msg, temp):
    issues = {"1": "damaged_product", "2": "order_issue", "3": "general_inquiry", "4": "talk_to_agent"}
    if msg not in issues:
        return "Reply 1, 2, 3, or 4."
    temp["issue_type"] = issues[msg]
    update_session(mobile, "awaiting_issue_description", temp)
    return f"*{issues[msg].replace(\'_\', \' \').title()}*\n\nDescribe your issue:"

def sup_desc(mobile, message, temp):
    if len(message.strip()) < 10:
        return "Please provide more detail:"
    temp["description"] = message.strip()
    user = get_user(mobile)
    ticket_id = create_ticket(user["customer_id"], temp["issue_type"], temp["description"])
    clear_session(mobile)
    return format_ticket_confirmation(ticket_id, temp["issue_type"]) + "\n\n" + get_main_menu()

def dist_name(mobile, message, temp):
    temp["biz_name"] = message.strip()
    update_session(mobile, "awaiting_biz_location", temp)
    return "Enter *Business Location* (City, State):"

def dist_loc(mobile, message, temp):
    temp["biz_location"] = message.strip()
    update_session(mobile, "awaiting_biz_experience", temp)
    return "Years of experience in distribution? (Enter number)"

def dist_exp(mobile, message, temp):
    try:
        years = int(message.strip())
    except ValueError:
        return "Enter a number (e.g. 3):"
    save_distributor_request(temp["biz_name"], temp["biz_location"], years, mobile)
    clear_session(mobile)
    return format_distributor_confirmation(temp["biz_name"]) + "\n\n" + get_main_menu()
'''

# Write all files
for filepath, content in files.items():
    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created: {filepath}")

print("\nAll files created successfully!")