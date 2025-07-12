import threading
import time
from datetime import datetime, timedelta
import re
from message import send_message
from whatsapp_utils.message_types import get_text_message_input
import dateparser

def parse_time_string(time_str):
    """
    Parses a wide range of natural language time expressions.
    Returns a datetime object for the reminder time, or None if invalid.
    """
    now = datetime.now()
    reminder_time = dateparser.parse(time_str, settings={'PREFER_DATES_FROM': 'future'})
    if reminder_time is None:
        return None
    # If the parsed time is in the past, try to adjust to the future
    if reminder_time < now:
        # If only time is given (e.g., "5:30pm"), dateparser may use today
        # If so, add a day
        if reminder_time.date() == now.date():
            reminder_time += timedelta(days=1)
        else:
            return None
    return reminder_time

def schedule_whatsapp_reminder(recipient: str, event: str, time_str: str):
    """
    Schedules a WhatsApp reminder message to be sent at a future time,
    via send_message / get_text_message_input.
    """
    reminder_time = parse_time_string(time_str)
    if not reminder_time:
        return {"result": "Invalid time format. Use '5:30pm', 'in 10 minutes', etc."}

    delta = reminder_time - datetime.now()
    if delta > timedelta(hours=24):
        return {"result": "Cannot set reminders more than 24 hours ahead."}

    def reminder_thread():
        secs = delta.total_seconds()
        if secs > 0:
            time.sleep(secs)
        msg_text = f"🔔 Reminder: {event} (scheduled at {reminder_time.strftime('%I:%M %p')})"
        structured = get_text_message_input(recipient, msg_text)
        send_message(structured)

    t = threading.Thread(target=reminder_thread, daemon=True)
    t.start()

    return {"result": f"Reminder set successfully at {reminder_time.strftime('%I:%M %p')}: {event}"}