import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from dateutil import tz
import dateparser
from message import send_message
from whatsapp_utils.message_types import get_text_message_input

# Use local timezone (e.g., IST for India)
LOCAL_TIMEZONE = tz.tzlocal()

def parse_time_string(time_str: str) -> Optional[datetime]:
    """
    Parses natural language time expressions into timezone-aware datetime.
    Returns a datetime object for the reminder time, or None if invalid.
    """
    if not time_str or not isinstance(time_str, str):
        return None

    try:
        now = datetime.now(LOCAL_TIMEZONE)
        reminder_time = dateparser.parse(time_str, settings={'PREFER_DATES_FROM': 'future'})

        if reminder_time is None:
            return None

        # Make reminder_time timezone-aware
        if reminder_time.tzinfo is None:
            reminder_time = reminder_time.replace(tzinfo=LOCAL_TIMEZONE)
        else:
            reminder_time = reminder_time.astimezone(LOCAL_TIMEZONE)

        # Adjust if parsed time is today but already passed
        if reminder_time < now:
            if reminder_time.date() == now.date():
                reminder_time += timedelta(days=1)
            else:
                return None

        return reminder_time

    except Exception as e:
        print(f"Error parsing time string '{time_str}': {str(e)}")
        return None

def schedule_whatsapp_reminder(recipient: str, event: str, time_str: str) -> Dict[str, Any]:
    """
    Schedules a WhatsApp reminder message to be sent at a future time.
    """
    if not recipient or not isinstance(recipient, str):
        return {"result": "Invalid recipient provided."}

    if not event or not isinstance(event, str):
        return {"result": "Invalid event description provided."}

    if not time_str or not isinstance(time_str, str):
        return {"result": "Invalid time format provided."}

    try:
        reminder_time = parse_time_string(time_str)
        if not reminder_time:
            return {
                "result": "Invalid time format. Try something like '5:30pm', 'in 10 minutes', or 'tomorrow at 3pm'."
            }

        now = datetime.now(LOCAL_TIMEZONE)
        delta = reminder_time - now

        if delta < timedelta(minutes=1):
            return {"result": "Reminders must be set at least 1 minute in the future."}
        if delta > timedelta(hours=24):
            return {"result": "Cannot set reminders more than 24 hours ahead."}

        def reminder_thread():
            try:
                secs = delta.total_seconds()
                if secs > 0:
                    time.sleep(secs)

                msg_text = f"🔔 Reminder: {event}"
                structured = get_text_message_input(recipient, msg_text)
                send_message(structured)

            except Exception as e:
                print(f"Error in reminder thread for {recipient}: {str(e)}")

        threading.Thread(target=reminder_thread, daemon=True).start()

        # Format reminder time clearly in local time
        return {
            "result": f"Reminder set successfully for {reminder_time.strftime('%I:%M %p on %B %d')}: {event}"
        }

    except Exception as e:
        print(f"Error scheduling reminder: {str(e)}")
        return {"result": "Failed to schedule reminder. Please try again."}
