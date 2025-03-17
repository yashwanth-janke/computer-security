import re
import json
import datetime
import bleach
from config import BLOCKED_PATTERNS, SENSITIVE_TOPICS

def is_pattern_match(text, patterns):
    """Check if text contains any of the blocked patterns."""
    # Convert to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    for pattern in patterns:
        if pattern.lower() in text_lower:
            return True, pattern
    
    return False, None

def check_input_length(text, max_length):
    """Check if input text exceeds maximum allowed length."""
    return len(text) <= max_length

def sanitize_html(text):
    """Remove HTML/JavaScript from text."""
    return bleach.clean(
        text,
        tags=[],  # Allow no HTML tags
        strip=True  # Strip disallowed tags
    )

def log_security_event(event_type, content, details, action_taken, log_file):
    """Log security events to a file."""
    log_entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "event_type": event_type,
        "content_excerpt": content[:100] + ("..." if len(content) > 100 else ""),
        "details": details,
        "action_taken": action_taken
    }
    
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    except Exception as e:
        print(f"Error logging security event: {e}")