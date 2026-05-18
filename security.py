# =============================================
# security.py
# Handles data security & input validation
# =============================================

import re
import hashlib
import os
from dotenv import load_dotenv

load_dotenv()


# -----------------------------------------------
# Validate mobile number format
# -----------------------------------------------
def is_valid_mobile(mobile):
    """
    Checks if mobile number is valid.
    Accepts formats: +919876543210 or 9876543210
    """
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, mobile.strip()))


# -----------------------------------------------
# Validate email format
# -----------------------------------------------
def is_valid_email(email):
    """
    Checks if email address is valid.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


# -----------------------------------------------
# Sanitize user input
# Removes dangerous characters that could
# cause SQL injection or code injection
# -----------------------------------------------
def sanitize_input(text):
    """
    Cleans user input by removing dangerous characters.
    Always use this before saving to database.
    """
    if not text:
        return ""

    # Remove SQL injection characters
    dangerous = ["'", '"', ";", "--", "/*", "*/", "xp_", "DROP", "DELETE", "INSERT", "UPDATE"]
    clean = text.strip()

    for char in dangerous:
        clean = clean.replace(char, "")

    # Limit length to prevent overflow
    return clean[:500]


# -----------------------------------------------
# Hash sensitive data (like passwords)
# -----------------------------------------------
def hash_data(data):
    """
    Creates a secure hash of sensitive data.
    Use for passwords or sensitive fields.
    """
    return hashlib.sha256(data.encode()).hexdigest()


# -----------------------------------------------
# Validate Twilio webhook signature
# Ensures requests are really from Twilio
# -----------------------------------------------
def is_valid_twilio_request(request):
    """
    Verifies that incoming webhook is from Twilio.
    Prevents fake/malicious requests.
    """
    try:
        from twilio.request_validator import RequestValidator
        validator = RequestValidator(os.getenv("TWILIO_AUTH_TOKEN"))

        signature = request.headers.get('X-Twilio-Signature', '')
        url       = request.url
        params    = request.form.to_dict()

        return validator.validate(url, params, signature)
    except Exception as e:
        print(f"Warning: Twilio validation error: {e}")
        return False


# -----------------------------------------------
# Rate limiting — prevent spam
# Tracks how many messages a user sends per minute
# -----------------------------------------------
message_counts = {}   # Stores {mobile: [timestamps]}

def is_rate_limited(mobile):
    """
    Returns True if user is sending too many messages.
    Limit: 20 messages per minute.
    """
    import time
    now      = time.time()
    one_min  = 60

    if mobile not in message_counts:
        message_counts[mobile] = []

    # Remove timestamps older than 1 minute
    message_counts[mobile] = [
        t for t in message_counts[mobile]
        if now - t < one_min
    ]

    # Check if over limit
    if len(message_counts[mobile]) >= 20:
        return True

    # Add current timestamp
    message_counts[mobile].append(now)
    return False