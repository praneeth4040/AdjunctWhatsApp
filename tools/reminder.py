import threading
import time
from datetime import datetime, timedelta
import re
from typing import Dict, Any, Optional
from message import send_message
from whatsapp_utils.message_types import get_text_message_input
import dateparser

def parse_time_string(time_str: str) -> Optional[datetime]:
    """
    Parses a wide range of natural language time expressions.
    Returns a datetime object for the reminder time, or None if invalid.
    
    Args:
        time_str: Natural language time expression (e.g., "5:30pm", "in 10 minutes")
        
    Returns:
        datetime object for the reminder time, or None if invalid
    """
    # Input validation
    if not time_str or not isinstance(time_str, str):
        return None
    
    try:
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
        
    except Exception as e:
        print(f"Error parsing time string '{time_str}': {str(e)}")
        return None

def schedule_whatsapp_reminder(recipient: str, event: str, time_str: str) -> Dict[str, Any]:
    """
    Schedules a WhatsApp reminder message to be sent at a future time.
    
    Args:
        recipient: The recipient's phone number
        event: The event/reminder description
        time_str: Natural language time expression
        
    Returns:
        Dictionary containing the result message
    """
    # Input validation
    if not recipient or not isinstance(recipient, str):
        return {"result": "Invalid recipient provided."}
    
    if not event or not isinstance(event, str):
        return {"result": "Invalid event description provided."}
    
    if not time_str or not isinstance(time_str, str):
        return {"result": "Invalid time format provided."}
    
    try:
        reminder_time = parse_time_string(time_str)
        if not reminder_time:
            return {"result": "Invalid time format. Use '5:30pm', 'in 10 minutes', 'tomorrow at 3pm', etc."}

        now = datetime.now()
        delta = reminder_time - now
        
        # Validate time range (between 1 minute and 24 hours)
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

        # Start the reminder thread
        t = threading.Thread(target=reminder_thread, daemon=True)
        t.start()

        return {"result": f"Reminder set successfully for {reminder_time.strftime('%I:%M %p on %B %d')}: {event}"}
        
    except Exception as e:
        print(f"Error scheduling reminder: {str(e)}")
        return {"result": "Failed to schedule reminder. Please try again."}