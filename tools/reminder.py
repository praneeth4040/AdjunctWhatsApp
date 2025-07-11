import threading
import time
from datetime import datetime, timedelta
import re

def parse_time_string(time_str):
    """
    Parses time_str which can be:
    - Absolute time: '5:30pm', '17:30'
    - Relative time: 'after 1 min', 'in 2 hours', 'after 30 seconds'
    Returns a datetime object for the reminder time, or None if invalid.
    """
    now = datetime.now()
    rel_pattern = r"(?:after|in) (\d+) (second|seconds|minute|minutes|hour|hours|day|days)"
    rel_match = re.search(rel_pattern, time_str, re.IGNORECASE)
    if rel_match:
        value = int(rel_match.group(1))
        unit = rel_match.group(2).lower()
        if 'second' in unit:
            delta = timedelta(seconds=value)
        elif 'minute' in unit:
            delta = timedelta(minutes=value)
        elif 'hour' in unit:
            delta = timedelta(hours=value)
        elif 'day' in unit:
            delta = timedelta(days=value)
        else:
            return None
        return now + delta
    for fmt in ["%I:%M%p", "%H:%M"]:
        try:
            reminder_time = datetime.strptime(time_str, fmt)
            reminder_time = now.replace(hour=reminder_time.hour, minute=reminder_time.minute, second=0, microsecond=0)
            if reminder_time < now:
                reminder_time += timedelta(days=1)
            return reminder_time
        except ValueError:
            continue
    return None

def set_reminder(event: str, time_str: str):
    """
    Sets a reminder for the user. Supports absolute times (e.g., '5:30pm', '17:30')
    and relative times (e.g., 'after 1 min', 'in 2 hours').
    Enforces a 24-hour limit.
    """
    now = datetime.now()
    reminder_time = parse_time_string(time_str)
    if not reminder_time:
        return {"result": "Invalid time format. Please use formats like '5:30pm', 'after 1 min', or 'in 2 hours'."}
    delta = reminder_time - now
    if delta > timedelta(hours=24):
        return {"result": "Unable to set reminder for more than 24 hours from now."}
    def reminder_thread():
        wait_seconds = delta.total_seconds()
        if wait_seconds > 0:
            time.sleep(wait_seconds)
        print(f"\n[REMINDER] {event} (at {reminder_time.strftime('%I:%M %p')})\n")
    t = threading.Thread(target=reminder_thread, daemon=True)
    t.start()
    return {"result": f"Reminder set for {reminder_time.strftime('%I:%M %p')}: {event}"} 