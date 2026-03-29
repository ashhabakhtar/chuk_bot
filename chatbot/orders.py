# =============================================
# chatbot/orders.py
# Handles order placement and tracking
# =============================================

from db import execute_query


# -----------------------------------------------
# Generate unique Order ID (e.g. PK-00042)
# -----------------------------------------------
def generate_order_id():
    rows = execute_query(
        "SELECT COUNT(*) as total FROM orders",
        fetch=True
    )
    count = rows[0]['total'] + 1 if rows else 1
    return f"PK-{str(count).zfill(5)}"    # PK-00001, PK-00002...


# -----------------------------------------------
# Place a new order
# -----------------------------------------------
def place_order(customer_id, product_id, quantity, delivery_location, business_name):
    order_id = generate_order_id()

    execute_query(
        """INSERT INTO orders 
           (order_id, customer_id, product_id, quantity, delivery_location, business_name, status)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (order_id, customer_id, product_id, quantity,
         delivery_location, business_name, 'processing')
    )
    return order_id


# -----------------------------------------------
# Track order by Order ID
# -----------------------------------------------
def track_by_order_id(order_id):
    rows = execute_query(
        """SELECT o.*, p.name as product_name 
           FROM orders o 
           JOIN products p ON o.product_id = p.product_id
           WHERE o.order_id = %s""",
        (order_id,),
        fetch=True
    )
    return rows[0] if rows else None


# -----------------------------------------------
# Track orders by mobile number
# -----------------------------------------------
def track_by_mobile(mobile):
    rows = execute_query(
        """SELECT o.*, p.name as product_name 
           FROM orders o 
           JOIN products p ON o.product_id = p.product_id
           JOIN users u ON o.customer_id = u.customer_id
           WHERE u.mobile = %s
           ORDER BY o.created_at DESC LIMIT 5""",
        (mobile,),
        fetch=True
    )
    return rows if rows else []


# -----------------------------------------------
# Format order confirmation message
# -----------------------------------------------
def format_order_confirmation(order_id, product_name, quantity, location):
    msg  = "✅ *Order Placed Successfully!*\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"📋 Order ID:  *{order_id}*\n"
    msg += f"📦 Product:   {product_name}\n"
    msg += f"🔢 Quantity:  {quantity} packs\n"
    msg += f"📍 Delivery:  {location}\n"
    msg += f"🔄 Status:    Processing\n\n"
    msg += "💬 Our sales team will contact you shortly.\n"
    msg += f"📌 Save your Order ID: *{order_id}*"
    return msg


# -----------------------------------------------
# Format order tracking message
# -----------------------------------------------
def format_tracking_message(order):
    status_emoji = {
        'processing':  '🔄',
        'confirmed':   '✅',
        'dispatched':  '🚚',
        'delivered':   '🎉',
        'cancelled':   '❌'
    }

    emoji = status_emoji.get(order['status'], '📋')

    msg  = f"📦 *Order Tracking*\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🆔 Order ID:  *{order['order_id']}*\n"
    msg += f"📦 Product:   {order['product_name']}\n"
    msg += f"🔢 Quantity:  {order['quantity']} packs\n"
    msg += f"📍 Location:  {order['delivery_location']}\n"
    msg += f"{emoji} Status:    *{order['status'].upper()}*\n"
    msg += f"📅 Date:      {order['created_at'].strftime('%d %b %Y')}\n"
    return msg