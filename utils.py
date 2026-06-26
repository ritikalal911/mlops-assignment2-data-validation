# utils.py
import pandas as pd
import re

def load_csv(filepath):
    """Load a CSV file and return a DataFrame."""
    df = pd.read_csv(filepath)
    if df.empty:
        raise ValueError("CSV file is empty")
    return df

def clean_phone(phone):
    """Normalize phone number to digits only (must be 10 digits)."""
    if not phone or not isinstance(phone, str):
        return None
    digits = re.sub(r"\D", "", phone)
    if len(digits) != 10:
        return None
    return digits

def validate_email(email):
    """Return True if email matches valid format."""
    if not email or not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return bool(re.match(pattern, email))