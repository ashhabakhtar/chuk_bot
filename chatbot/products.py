# =============================================
# chatbot/products.py
# Handles product browsing and display
# =============================================

from db import execute_query


# -----------------------------------------------
# Get all unique categories
# -----------------------------------------------
def get_categories():
    rows = execute_query(
        "SELECT DISTINCT category FROM products WHERE stock_available = TRUE",
        fetch=True
    )
    return [row['category'] for row in rows] if rows else []


# -----------------------------------------------
# Get products by category
# -----------------------------------------------
def get_products_by_category(category):
    rows = execute_query(
        "SELECT * FROM products WHERE category = %s AND stock_available = TRUE",
        (category,),
        fetch=True
    )
    return rows if rows else []


# -----------------------------------------------
# Get single product by ID
# -----------------------------------------------
def get_product_by_id(product_id):
    rows = execute_query(
        "SELECT * FROM products WHERE product_id = %s",
        (product_id,),
        fetch=True
    )
    return rows[0] if rows else None


# -----------------------------------------------
# Format category list as WhatsApp message
# -----------------------------------------------
def format_categories_message():
    categories = get_categories()
    if not categories:
        return "❌ No products available right now."

    msg = "🛍️ *CHUK Product Categories*\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"

    for i, cat in enumerate(categories, 1):
        msg += f"  {i}. {cat}\n"

    msg += "\n📌 Reply with the *number* to browse that category.\n"
    msg += "0️⃣  Reply *0* to go back to Main Menu"
    return msg


# -----------------------------------------------
# Format product list as WhatsApp message
# -----------------------------------------------
def format_products_message(category):
    products = get_products_by_category(category)
    if not products:
        return f"❌ No products found in {category}."

    msg = f"📦 *{category} Products*\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"

    for p in products:
        msg += f"🔹 *{p['name']}*\n"
        msg += f"   • Size: {p['size']}\n"
        msg += f"   • Weight: {p['weight_grams']}g\n"
        msg += f"   • Pack of: {p['packaging_qty']} units\n"
        msg += f"   • Price: ₹{p['price_per_pack']} per pack\n"
        msg += f"   • ID: #{p['product_id']}\n\n"

    msg += "📌 Reply with product *ID number* to place an order.\n"
    msg += "0️⃣  Reply *0* to go back"
    return msg