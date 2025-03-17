import re
from security.security_utils import sanitize_html, is_pattern_match, check_input_length
from config import BLOCKED_PATTERNS, SENSITIVE_TOPICS, MAX_INPUT_LENGTH

class InputSanitizer:
    """Class to sanitize and validate user inputs."""
    
    @staticmethod
    def sanitize_input(text):
        """
        Sanitize user input by removing HTML and normalizing whitespace.
        
        Args:
            text (str): Raw user input
            
        Returns:
            str: Sanitized text
        """
        # Strip HTML
        sanitized = sanitize_html(text)
        
        # Normalize whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        return sanitized
    
    @staticmethod
    def validate_input(text):
        """
        Validate user input against security rules.
        
        Args:
            text (str): Sanitized user input
            
        Returns:
            tuple: (is_valid, reason)
        """
        # Check length
        if not check_input_length(text, MAX_INPUT_LENGTH):
            return False, f"Input exceeds maximum length of {MAX_INPUT_LENGTH} characters"
        
        # Check for blocked patterns
        has_blocked, pattern = is_pattern_match(text, BLOCKED_PATTERNS)
        if has_blocked:
            return False, f"Input contains potentially harmful pattern: '{pattern}'"
        
        # Check for sensitive topics
        has_sensitive, topic = is_pattern_match(text, SENSITIVE_TOPICS)
        if has_sensitive:
            return False, f"Input contains sensitive topic: '{topic}'"
        
        return True, "Input validated"