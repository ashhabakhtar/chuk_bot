# =============================================
# chatbot/auth.py
# Handles user registration, login, OTP
# =============================================

from db import execute_query
from twilio.rest import Client
from dotenv import load_dotenv
import os, random

load_dotenv()

# -----------------------------------------------
# HELPER: Generate 6-digit OTP
# -----------------------------------------------
def generate_otp():
    return str(random.randint(100000, 999999))


# -----------------------------------------------
# HELPER: Send OTP via Twilio SMS
# -----------------------------------------------
def send_otp(mobile, otp):
    """
    Sends OTP to user's mobile number via SMS.
    mobile = phone number like +919876543210
    """
    try:
        client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN")
        )
        client.messages.create(
            body=f"Your CHUK verification code is: {otp}. Valid for 5 minutes.",
            from_=os.getenv("TWILIO_WHATSAPP_NUMBER"),
            to=f"whatsapp:{mobile}"
        )
        return True
    except Exception as e:
        print(f"❌ OTP send failed: {e}")
        return False


# -----------------------------------------------
# Check if user already exists in database
# -----------------------------------------------
def user_exists(mobile):
    rows = execute_query(
        "SELECT customer_id FROM users WHERE mobile = %s",
        (mobile,),
        fetch=True
    )
    return len(rows) > 0 if rows else False


# -----------------------------------------------
# Get user details from database
# -----------------------------------------------
def get_user(mobile):
    rows = execute_query(
        "SELECT * FROM users WHERE mobile = %s",
        (mobile,),
        fetch=True
    )
    return rows[0] if rows else None


# -----------------------------------------------
# Generate unique Customer ID (e.g. CHUK-00042)
# -----------------------------------------------
def generate_customer_id():
    rows = execute_query(
        "SELECT COUNT(*) as total FROM users",
        fetch=True
    )
    count = rows[0]['total'] + 1 if rows else 1
    return f"CHUK-{str(count).zfill(5)}"   # CHUK-00001, CHUK-00002...


# -----------------------------------------------
# Save new user to database
# -----------------------------------------------
def register_user(name, email, mobile, customer_type):
    customer_id = generate_customer_id()

    # Generate and store OTP for verification
    otp = generate_otp()

    execute_query(
        """INSERT INTO users 
           (customer_id, name, email, mobile, customer_type, otp, is_verified)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (customer_id, name, email, mobile, customer_type, otp, False)
    )

    # Send OTP to user
    send_otp(mobile, otp)

    return customer_id, otp


# -----------------------------------------------
# Verify OTP entered by user
# -----------------------------------------------
def verify_otp(mobile, entered_otp):
    rows = execute_query(
        "SELECT otp FROM users WHERE mobile = %s",
        (mobile,),
        fetch=True
    )

    if rows and rows[0]['otp'] == entered_otp:
        # Mark user as verified
        execute_query(
            "UPDATE users SET is_verified = TRUE, otp = NULL WHERE mobile = %s",
            (mobile,)
        )
        return True
    return False