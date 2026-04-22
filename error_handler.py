# =============================================
# error_handler.py
# Handles all errors gracefully
# App never crashes — always replies to user
# =============================================

import traceback
from datetime import datetime


# -----------------------------------------------
# Log errors to a file
# -----------------------------------------------
def log_error(error, context=""):
    """
    Saves error details to errors.log file.
    So you can review what went wrong later.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = f"\n[{timestamp}] {context}\n{traceback.format_exc()}\n"

    print(f"Error: ERROR: {error}")   # Show in terminal

    # Save to log file
    try:
        with open("errors.log", "a") as f:
            f.write(error_msg)
    except:
        pass   # Don't crash while logging errors


# -----------------------------------------------
# Safe message handler wrapper
# Wraps handle_message so it NEVER crashes
# -----------------------------------------------
def safe_handle(func, sender, message):
    """
    Safely calls a function.
    If it crashes, returns a friendly error message
    instead of a 500 server error.
    """
    try:
        return func(sender, message)
    except Exception as e:
        log_error(e, f"sender={sender}, message={message}")
        return (
            "⚠️ Sorry, something went wrong on our end.\n\n"
            "Please try again or send *Hi* to restart.\n"
            "If issue persists, contact support."
        )


# -----------------------------------------------
# Database error handler
# -----------------------------------------------
def handle_db_error(error, operation=""):
    """
    Handles database connection or query errors.
    """
    log_error(error, f"DB operation: {operation}")
    return None   # Return None so calling code can handle gracefully


# -----------------------------------------------
# Friendly messages for common errors
# -----------------------------------------------
def get_friendly_error(error_type):
    messages = {
        'db_down':        "⚠️ Our system is temporarily unavailable. Please try again in a few minutes.",
        'invalid_input':  "❌ Invalid input. Please check and try again.",
        'otp_expired':    "⏰ OTP has expired. Reply RESEND to get a new one.",
        'order_failed':   "❌ Order could not be placed. Please try again.",
        'not_found':      "🔍 No records found for your query.",
        'rate_limit':     "⏳ Too many messages! Please wait a moment before trying again.",
        'general':        "⚠️ Something went wrong. Send *Hi* to restart."
    }
    return messages.get(error_type, messages['general'])