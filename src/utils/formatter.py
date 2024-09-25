import re
from datetime import datetime
from urllib.parse import quote
from bs4 import BeautifulSoup


def strip_html(html_content):
    """Remove HTML tags and extract text content."""
    soup = None
    if html_content:
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
        except Exception as e:
            raise e
        return soup.get_text(separator=' ', strip=True)
    else:
        return None

def clean_whitespace(text):
    """Remove excessive whitespace and newlines."""
    return re.sub(r'\s+', ' ', text).strip()


def timestamp_to_datetime(timestamp_ms):
    # Convert milliseconds to seconds
    timestamp_s = int(timestamp_ms) / 1000

    # Create datetime object
    dt_object = datetime.fromtimestamp(timestamp_s)

    # Format datetime object to desired string format
    formatted_time = dt_object.strftime('%Y-%m-%dT%H:%M:%SZ')

    return formatted_time


def encode_urls(text):
    if not text:
        return None
    # Regular expression pattern to match URLs
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

    def replace_url(match):
        url = match.group()
        encoded_url = quote(url, safe=':/')
        return encoded_url

    encoded_text = url_pattern.sub(replace_url, text)
    return encoded_text


def apply_all_formats(html_content):
    """Extract meaningful text from HTML content."""
    step_1 = strip_html(html_content)
    step_2 = encode_urls(step_1)
    return step_2







