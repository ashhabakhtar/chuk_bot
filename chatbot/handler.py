# =============================================
# chatbot/handler.py — THE BRAIN
# Handles every incoming WhatsApp message
# =============================================

from chatbot.session_manager import get_session, update_session, clear_session
from chatbot.auth          import user_exists, get_user, register_user, verify_otp, generate_otp, send_otp
from chatbot.products      import get_categories, get_product_by_id, format_categories_message, format_products_message
from chatbot.orders        import place_order, track_by_order_id, track_by_mobile, format_order_confirmation, format_tracking_message
from chatbot.support       import create_ticket, format_ticket_confirmation
from chatbot.distributor   import save_distributor_request, format_distributor_confirmation


def handle_message(sender, message):
    mobile = sender.replace("whatsapp:", "")
    session = get_session(mobile)
    step    = session['current_step']
    temp    = session['temp_data']
    msg     = message.strip().lower()

    # Global commands
    if msg in ['hi', 'hello', 'hey', 'start', 'menu', '0']:
        return handle_start(mobile, msg)
    if msg == 'cancel':
        clear_session(mobile)
        return "Cancelled.\n\n" + get_main_menu()

    # Route by step
    if step == 'new_user':                    return handle_start(mobile, msg)
    elif step == 'awaiting_name':             return reg_collect_name(mobile, message, temp)
    elif step == 'awaiting_email':            return reg_collect_email(mobile, message, temp)
    elif step == 'awaiting_customer_type':    return reg_collect_type(mobile, message, temp)
    elif step == 'awaiting_otp':              return reg_verify_otp(mobile, message, temp)
    elif step == 'main_menu':                 return handle_main_menu(mobile, msg, temp)
    elif step == 'browsing_categories':       return handle_category_selection(mobile, msg)
    elif step == 'browsing_products':         return handle_product_selection(mobile, msg, temp)
    elif step == 'awaiting_order_quantity':   return order_collect_quantity(mobile, message, temp)
    elif step == 'awaiting_delivery_location':return order_collect_location(mobile, message, temp)
    elif step == 'awaiting_business_name':    return order_collect_business(mobile, message, temp)
    elif step == 'confirm_order':             return order_confirm(mobile, msg, temp)
    elif step == 'awaiting_tracking_input':   return handle_tracking(mobile, message)
    elif step == 'awaiting_issue_type':       return support_collect_issue(mobile, msg, temp)
    elif step == 'awaiting_issue_description':return support_collect_description(mobile, message, temp)
    elif step == 'awaiting_biz_name':         return dist_collect_biz_name(mobile, message, temp)
    elif step == 'awaiting_biz_location':     return dist_collect_location(mobile, message, temp)
    elif step == 'awaiting_biz_experience':   return dist_collect_experience(mobile, message, temp)
    else:
        clear_session(mobile)
        return "Session reset.\n\n" + get_main_menu()


def handle_start(mobile, msg):
    if user_exists(mobile):
        user = get_user(mobile)
        update_session(mobile, 'main_menu')
        return f"Welcome back, *{user['name']}*!\nCustomer ID: {user['customer_id']}\n\n" + get_main_menu()
    else:
        update_session(mobile, 'awaiting_name')
        return "Welcome to *CHUK by Pakka Ltd*!\n\nLet's register you first.\n\nEnter your *Full Name*:"


def get_main_menu():
    return (
        "*Main Menu*\n"
        "1 - View Products\n"
        "2 - Place Order\n"
        "3 - Track My Order\n"
        "4 - Become a Distributor\n"
        "5 - Customer Support\n\n"
        "Reply with a number (1-5)"
    )


def handle_main_menu(mobile, msg, temp):
    if msg == '1':
        update_session(mobile, 'browsing_categories')
        return format_categories_message()
    elif msg == '2':
        update_session(mobile, 'browsing_categories', {'ordering': True})
        return "Place an Order - select a product:\n\n" + format_categories_message()
    elif msg == '3':
        update_session(mobile, 'awaiting_tracking_input')
        return "Enter your Order ID (e.g. PK-00001) or mobile number:"
    elif msg == '4':
        update_session(mobile, 'awaiting_biz_name')
        return "Become a Distributor!\n\nEnter your *Business Name*:"
    elif msg == '5':
        update_session(mobile, 'awaiting_issue_type')
        return "Customer Support:\n1 - Damaged Product\n2 - Order Issue\n3 - General Inquiry\n4 - Talk to Agent\n\nReply 1-4"
    else:
        return "Invalid option.\n\n" + get_main_menu()


def reg_collect_name(mobile, message, temp):
    if len(message.strip()) < 2:
        return "Name too short. Enter your full name:"
    temp['name'] = message.strip()
    update_session(mobile, 'awaiting_email', temp)
    return f"Name saved: *{temp['name']}*\n\nEnter your *Email Address*:"


def reg_collect_email(mobile, message, temp):
    if '@' not in message or '.' not in message:
        return "Invalid email. Try again:"
    temp['email'] = message.strip().lower()
    update_session(mobile, 'awaiting_customer_type', temp)
    return "Select *Customer Type*:\n1 - Retailer\n2 - Wholesaler\n3 - Individual\n\nReply 1, 2 or 3"


def reg_collect_type(mobile, message, temp):
    types = {'1': 'retailer', '2': 'wholesaler', '3': 'individual'}
    if message.strip() not in types:
        return "Reply with 1, 2, or 3 only."
    temp['customer_type'] = types[message.strip()]
    customer_id, otp = register_user(temp['name'], temp['email'], mobile, temp['customer_type'])
    temp['customer_id'] = customer_id
    update_session(mobile, 'awaiting_otp', temp)
    return f"OTP sent to *{mobile}*\n\nEnter the *6-digit OTP*:"


def reg_verify_otp(mobile, message, temp):
    if verify_otp(mobile, message.strip()):
        update_session(mobile, 'main_menu')
        return f"Registration Successful!\nCustomer ID: *{temp.get('customer_id')}*\n\nWelcome to CHUK!\n\n" + get_main_menu()
    else:
        return "Invalid OTP. Try again:\n(Reply RESEND for a new OTP)"


def handle_category_selection(mobile, msg):
    if msg == '0':
        update_session(mobile, 'main_menu')
        return get_main_menu()
    categories = get_categories()
    try:
        index = int(msg) - 1
        if 0 <= index < len(categories):
            selected = categories[index]
            session  = get_session(mobile)
            temp     = session['temp_data']
            temp['selected_category'] = selected
            update_session(mobile, 'browsing_products', temp)
            return format_products_message(selected)
        else:
            return "Invalid option.\n\n" + format_categories_message()
    except ValueError:
        return "Reply with a number.\n\n" + format_categories_message()


def handle_product_selection(mobile, msg, temp):
    if msg == '0':
        update_session(mobile, 'browsing_categories', temp)
        return format_categories_message()
    try:
        product = get_product_by_id(int(msg))
        if product:
            temp['product_id']   = product['product_id']
            temp['product_name'] = product['name']
            update_session(mobile, 'awaiting_order_quantity', temp)
            return f"Selected: *{product['name']}*\nPrice: Rs.{product['price_per_pack']} per pack\n\nEnter *Quantity* (packs):"
        else:
            return "Product not found. Enter a valid product ID."
    except ValueError:
        return "Enter the product ID number."


def order_collect_quantity(mobile, message, temp):
    try:
        qty = int(message.strip())
        if qty <= 0:
            return "Quantity must be at least 1:"
        temp['quantity'] = qty
        update_session(mobile, 'awaiting_delivery_location', temp)
        return "Enter your *Delivery Address* (city + full address):"
    except ValueError:
        return "Enter a valid number:"


def order_collect_location(mobile, message, temp):
    if len(message.strip()) < 5:
        return "Please enter a complete address:"
    temp['delivery_location'] = message.strip()
    update_session(mobile, 'awaiting_business_name', temp)
    return "Enter your *Business Name* (or type NA):"


def order_collect_business(mobile, message, temp):
    temp['business_name'] = message.strip()
    update_session(mobile, 'confirm_order', temp)
    product = get_product_by_id(temp['product_id'])
    total   = product['price_per_pack'] * temp['quantity']
    return (
        f"*Order Summary*\n"
        f"Product:  {temp['product_name']}\n"
        f"Quantity: {temp['quantity']} packs\n"
        f"Total:    Rs.{total}\n"
        f"Delivery: {temp['delivery_location']}\n"
        f"Business: {temp['business_name']}\n\n"
        "Reply *YES* to confirm or *NO* to cancel"
    )


def order_confirm(mobile, msg, temp):
    if msg == 'yes':
        user     = get_user(mobile)
        order_id = place_order(user['customer_id'], temp['product_id'], temp['quantity'], temp['delivery_location'], temp['business_name'])
        clear_session(mobile)
        return format_order_confirmation(order_id, temp['product_name'], temp['quantity'], temp['delivery_location']) + "\n\n" + get_main_menu()
    elif msg == 'no':
        clear_session(mobile)
        return "Order cancelled.\n\n" + get_main_menu()
    else:
        return "Reply YES to confirm or NO to cancel."


def handle_tracking(mobile, message):
    query = message.strip()
    if query.upper().startswith('PK-'):
        order = track_by_order_id(query.upper())
        if order:
            clear_session(mobile)
            return format_tracking_message(order) + "\n\n" + get_main_menu()
        return f"No order found with ID {query.upper()}"
    else:
        orders = track_by_mobile(query)
        if orders:
            clear_session(mobile)
            reply = "Your Recent Orders:\n\n"
            for o in orders:
                reply += format_tracking_message(o) + "\n---\n"
            return reply + "\n" + get_main_menu()
        return "No orders found. Try your Order ID (e.g. PK-00001)"


def support_collect_issue(mobile, msg, temp):
    issues = {'1': 'damaged_product', '2': 'order_issue', '3': 'general_inquiry', '4': 'talk_to_agent'}
    if msg not in issues:
        return "Reply with 1, 2, 3, or 4."
    temp['issue_type'] = issues[msg]
    update_session(mobile, 'awaiting_issue_description', temp)
    return f"*{issues[msg].replace('_',' ').title()}*\n\nDescribe your issue in detail:"


def support_collect_description(mobile, message, temp):
    if len(message.strip()) < 10:
        return "Please provide more detail:"
    temp['description'] = message.strip()
    user      = get_user(mobile)
    ticket_id = create_ticket(user['customer_id'], temp['issue_type'], temp['description'])
    clear_session(mobile)
    return format_ticket_confirmation(ticket_id, temp['issue_type']) + "\n\n" + get_main_menu()


def dist_collect_biz_name(mobile, message, temp):
    temp['biz_name'] = message.strip()
    update_session(mobile, 'awaiting_biz_location', temp)
    return "Enter your *Business Location* (City, State):"


def dist_collect_location(mobile, message, temp):
    temp['biz_location'] = message.strip()
    update_session(mobile, 'awaiting_biz_experience', temp)
    return "Years of experience in distribution? (Enter a number)"


def dist_collect_experience(mobile, message, temp):
    try:
        years = int(message.strip())
    except ValueError:
        return "Enter a number (e.g. 3):"
    save_distributor_request(temp['biz_name'], temp['biz_location'], years, mobile)
    clear_session(mobile)
    return format_distributor_confirmation(temp['biz_name']) + "\n\n" + get_main_menu()