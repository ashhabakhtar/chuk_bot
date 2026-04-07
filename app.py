# =============================================
# app.py — Main Entry Point (SECURE VERSION)
# Replace your existing app.py with this
# =============================================

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

from chatbot.handler  import handle_message
from security         import is_rate_limited, sanitize_input
from error_handler    import safe_handle, get_friendly_error


@app.route("/webhook", methods=["POST"])
def webhook():
    incoming_msg = request.form.get("Body", "").strip()
    sender       = request.form.get("From", "")
    mobile       = sender.replace("whatsapp:", "")

    print(f"📩 Message from {sender}: {incoming_msg}")

    # Rate limiting check
    if is_rate_limited(mobile):
        reply_text = get_friendly_error('rate_limit')

    # Empty message check
    elif not incoming_msg:
        reply_text = "Please send a text message."

    else:
        # Sanitize then handle
        clean_msg  = sanitize_input(incoming_msg)
        reply_text = safe_handle(handle_message, sender, clean_msg)

    resp = MessagingResponse()
    resp.message().body(reply_text)
    return str(resp)


@app.route("/", methods=["GET"])
def home():
    return "✅ CHUK Chatbot Server is Running!", 200


@app.errorhandler(404)
def not_found(e):
    return "❌ Route not found", 404

@app.errorhandler(500)
def server_error(e):
    return "❌ Internal server error", 500


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    print(f"Server starting on port {port}...")
    app.run(debug=True, port=port)