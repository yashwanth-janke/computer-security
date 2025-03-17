import re
from security.security_utils import sanitize_html, is_pattern_match

class OutputSanitizer:
    """Class to sanitize AI outputs before returning to users."""
    
    @staticmethod
    def sanitize_output(text):
        """
        Sanitize AI output by removing HTML and ensuring it's safe.
        
        Args:
            text (str): Raw AI output
            
        Returns:
            str: Sanitized text
        """
        # Strip HTML
        sanitized = sanitize_html(text)
        
        # Remove potential PII patterns (credit cards, SSNs, etc.)
        sanitized = OutputSanitizer._redact_pii(sanitized)
        
        return sanitized
    
    @staticmethod
    def _redact_pii(text):
        """Redact potential personally identifiable information."""
        # Credit card numbers
        text = re.sub(r'\b(?:\d{4}[- ]?){3}\d{4}\b', '[REDACTED CARD NUMBER]', text)
        
        # Social Security Numbers
        text = re.sub(r'\b\d{3}[-]?\d{2}[-]?\d{4}\b', '[REDACTED SSN]', text)
        
        # Email addresses - simple pattern
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[REDACTED EMAIL]', text)
        
        # Phone numbers - simple pattern
        text = re.sub(r'\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', '[REDACTED PHONE]', text)
        
        return text
    
    @staticmethod
    def validate_output(text):
        """
        Validate AI output for any security issues.
        
        Args:
            text (str): AI output to validate
            
        Returns:
            tuple: (is_valid, reason)
        """
        # Check for executable code blocks
        code_blocks = re.findall(r'```(?:python|javascript|java|c\+\+|bash|sh|ruby|perl|php)(.+?)```', 
                                text, re.DOTALL)
        
        if code_blocks and any(
            'import os' in block or 
            'subprocess' in block or 
            'eval(' in block or 
            'exec(' in block or
            'system(' in block
            for block in code_blocks
        ):
            return False, "Output contains potentially unsafe code execution"
            
        # Check if output is trying to impersonate system messages
        if re.search(r'(^|\n)System:', text, re.IGNORECASE):
            return False, "Output contains system impersonation"
            
        return True, "Output validated"