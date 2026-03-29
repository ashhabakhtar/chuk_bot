# =============================================
# chatbot/distributor.py
# Handles distributor registration requests
# =============================================

from db import execute_query


# -----------------------------------------------
# Save distributor request
# -----------------------------------------------
def save_distributor_request(business_name, location, experience, mobile, email=""):
    execute_query(
        """INSERT INTO distributor_requests 
           (business_name, location, experience_years, contact_mobile, contact_email, status)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (business_name, location, experience, mobile, email, 'pending')
    )


# -----------------------------------------------
# Format confirmation message
# -----------------------------------------------
def format_distributor_confirmation(business_name):
    msg  = "🤝 *Distributor Request Submitted!*\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🏢 Business: {business_name}\n"
    msg += f"🔄 Status:   Under Review\n\n"
    msg += "👨‍💼 Our sales team will review your request and\n"
    msg += "contact you within 2-3 business days.\n\n"
    msg += "Thank you for your interest in CHUK! 🌟"
    return msg