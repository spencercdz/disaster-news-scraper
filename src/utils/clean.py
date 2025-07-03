import re
from dateutil import parser as date_parser

def clean_text(text):
    if not text:
        return None
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return date_parser.parse(date_str).isoformat()
    except Exception:
        return None 