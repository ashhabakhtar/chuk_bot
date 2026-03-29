# =============================================
# chatbot/session_manager.py
# Tracks where each user is in the conversation
# =============================================

from db import execute_query
import json

def get_session(mobile):
    """
    Gets the current session/state for a user.
    Returns their current_step and any temporary data.
    """
    rows = execute_query(
        "SELECT current_step, temp_data FROM sessions WHERE mobile = %s",
        (mobile,),
        fetch=True
    )

    if rows:
        temp = rows[0]['temp_data']
        return {
            'current_step': rows[0]['current_step'],
            'temp_data': json.loads(temp) if temp else {}
        }
    else:
        # New user — create a fresh session
        execute_query(
            "INSERT INTO sessions (mobile, current_step, temp_data) VALUES (%s, %s, %s)",
            (mobile, 'new_user', '{}')
        )
        return {'current_step': 'new_user', 'temp_data': {}}


def update_session(mobile, step, temp_data=None):
    """
    Updates the user's current step and temporary data.
    step      = where user is now (e.g. 'awaiting_name')
    temp_data = dictionary of temporary inputs collected so far
    """
    execute_query(
        "UPDATE sessions SET current_step = %s, temp_data = %s WHERE mobile = %s",
        (step, json.dumps(temp_data or {}), mobile)
    )


def clear_session(mobile):
    """
    Resets the user's session back to main menu.
    Called when a flow is completed or user wants to restart.
    """
    execute_query(
        "UPDATE sessions SET current_step = %s, temp_data = %s WHERE mobile = %s",
        ('main_menu', '{}', mobile)
    )