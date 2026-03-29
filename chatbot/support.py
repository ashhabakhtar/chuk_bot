# =============================================
# chatbot/support.py
# Handles customer support tickets
# =============================================

from db import execute_query


# -----------------------------------------------
# Generate unique Ticket ID (e.g. PK-T0042)
# -----------------------------------------------
def generate_ticket_id():
    rows = execute_query(
        "SELECT COUNT(*) as total FROM tickets",
        fetch=True
    )
    count = rows[0]['total'] + 1 if rows else 1
    return f"PK-T{str(count).zfill(4)}"   # PK-T0001, PK-T0002...


# -----------------------------------------------
# Create a new support ticket
# -----------------------------------------------
def create_ticket(customer_id, issue_type, description):
    ticket_id = generate_ticket_id()

    execute_query(
        """INSERT INTO tickets 
           (ticket_id, customer_id, issue_type, description, status)
           VALUES (%s, %s, %s, %s, %s)""",
        (ticket_id, customer_id, issue_type, description, 'open')
    )
    return ticket_id


# -----------------------------------------------
# Format ticket confirmation message
# -----------------------------------------------
def format_ticket_confirmation(ticket_id, issue_type):
    msg  = "🎫 *Support Ticket Created!*\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━\n\n"
    msg += f"🆔 Ticket ID:  *{ticket_id}*\n"
    msg += f"📋 Issue Type: {issue_type.replace('_', ' ').title()}\n"
    msg += f"🔄 Status:     Open\n\n"
    msg += "👨‍💼 Our support team will contact you within 24 hours.\n"
    msg += f"📌 Save your Ticket ID: *{ticket_id}*"
    return msg