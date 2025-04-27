import random
import string

def generate_trip_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def get_current_time():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def generate_activity_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))