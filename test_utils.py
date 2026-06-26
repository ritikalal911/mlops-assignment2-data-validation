# test_utils.py
import pytest
import pandas as pd
from utils import load_csv, clean_phone, validate_email

# ════════════════════════════════════════
# Tests for load_csv()
# ════════════════════════════════════════

def test_load_csv_file_not_found():
    """Should raise FileNotFoundError for missing file."""
    with pytest.raises(FileNotFoundError):
        load_csv("nonexistent_file.csv")

def test_load_csv_empty_file(tmp_path):
    """Should raise ValueError for empty CSV."""
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("customer_id,age,email\n")
    with pytest.raises(ValueError, match="empty"):
        load_csv(str(empty_file))

def test_load_csv_success():
    """Should return a DataFrame with rows for valid CSV."""
    df = load_csv("customer_data.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    assert "customer_id" in df.columns

# ════════════════════════════════════════
# Tests for clean_phone()
# ════════════════════════════════════════

def test_clean_phone_dashes():
    assert clean_phone("123-456-7890") == "1234567890"

def test_clean_phone_dots():
    assert clean_phone("123.456.7890") == "1234567890"

def test_clean_phone_parentheses():
    assert clean_phone("(123) 456-7890") == "1234567890"

def test_clean_phone_plain_digits():
    assert clean_phone("1234567890") == "1234567890"

def test_clean_phone_too_short():
    assert clean_phone("12345") is None

def test_clean_phone_negative():
    assert clean_phone("-8437") is None

def test_clean_phone_none_input():
    assert clean_phone(None) is None

# ════════════════════════════════════════
# Tests for validate_email()
# ════════════════════════════════════════

def test_validate_email_valid():
    assert validate_email("user@example.com") is True

def test_validate_email_subdomain():
    assert validate_email("user@mail.example.com") is True

def test_validate_email_missing_at():
    assert validate_email("userdomain.com") is False

def test_validate_email_missing_domain():
    assert validate_email("user@") is False

def test_validate_email_starts_with_at():
    assert validate_email("@domain.com") is False

def test_validate_email_double_at():
    assert validate_email("user@@domain.com") is False

def test_validate_email_empty_string():
    assert validate_email("") is False

def test_validate_email_none():
    assert validate_email(None) is False