import re
import nltk

# Download required NLTK data on first run
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class PromptInjectionDetector:
    """Detects potential prompt injection attacks."""
    
    def __init__(self):
        # Common prompt injection indicators
        self.command_words = [
            "ignore", "disregard", "forget", "bypass", "override",
            "instead", "don't follow", "system prompt", "new instructions"
        ]
        
        # Compiled regex patterns for efficiency
        self.command_pattern = re.compile(
            r'\b(' + '|'.join(self.command_words) + r')\b', 
            re.IGNORECASE
        )
        
        # Detect delimiters that might be used to structure system prompts
        self.delimiter_pattern = re.compile(
            r'[\[\]\{\}\(\)<>"""\'\']+|--+|==+|\*\*+|##+'
        )
        
        # Detect attempts to impersonate system or trigger special modes
        self.impersonation_pattern = re.compile(
            r'\b(system:|user:|assistant:|as an AI|developer mode|DAN|root)\b',
            re.IGNORECASE
        )
    
    def detect_injection(self, text):
        """
        Analyzes text for potential prompt injection attempts.
        
        Args:
            text (str): User input text
            
        Returns:
            tuple: (is_injection, confidence, reason)
        """
        # Initialize scoring
        injection_score = 0
        reasons = []
        
        # Break input into sentences for context analysis
        sentences = nltk.sent_tokenize(text)
        
        # Check for command words
        command_matches = self.command_pattern.findall(text)
        if command_matches:
            injection_score += len(command_matches) * 2
            reasons.append(f"Command words detected: {', '.join(set(command_matches))}")
        
        # Check for delimiter patterns
        delimiter_matches = self.delimiter_pattern.findall(text)
        if len(delimiter_matches) > 3:  # Allow some normal usage
            injection_score += 1
            reasons.append("Multiple delimiter patterns detected")
            
        # Check for impersonation attempts
        impersonation_matches = self.impersonation_pattern.findall(text)
        if impersonation_matches:
            injection_score += len(impersonation_matches) * 3
            reasons.append(f"Potential impersonation detected: {', '.join(set(impersonation_matches))}")
        
        # Context analysis
        for i, sentence in enumerate(sentences):
            # Check for instructions directed at the AI system
            if re.search(r'\b(you should|you must|you need to|never|always)\b', sentence, re.IGNORECASE):
                if i == 0 or i == len(sentences) - 1:  # First or last sentence
                    injection_score += 1
                    reasons.append("Directive language in prominent position")
        
        # Calculate confidence based on score
        confidence = min(injection_score / 10, 1.0)
        
        # Determine if this is likely an injection attempt
        is_injection = confidence > 0.5
        
        return is_injection, confidence, reasons