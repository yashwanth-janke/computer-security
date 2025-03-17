from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
from config import LOG_FILE

# Import security components
from security.input_sanitizer import InputSanitizer
from security.output_sanitizer import OutputSanitizer
from security.prompt_injection import PromptInjectionDetector
from security.threat_monitor import ThreatMonitor
from security.security_utils import log_security_event

# Import LLM service
from services.llm_service import LLMService

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = os.urandom(24)

# Initialize components
input_sanitizer = InputSanitizer()
output_sanitizer = OutputSanitizer()
injection_detector = PromptInjectionDetector()
threat_monitor = ThreatMonitor()
llm_service = LLMService()

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/logs')
def logs():
    """Render the security logs page."""
    recent_threats = threat_monitor.get_recent_threats(limit=100)
    return render_template('logs.html', threats=recent_threats)

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Process chat requests through the security middleware.
    
    This endpoint:
    1. Checks rate limits
    2. Sanitizes input
    3. Detects prompt injections
    4. Calls the LLM
    5. Sanitizes output
    6. Returns the response
    """
    # Get client IP for rate limiting
    client_ip = request.remote_addr
    
    # Check rate limits
    is_allowed, reason = threat_monitor.check_rate_limit(client_ip)
    if not is_allowed:
        return jsonify({
            'success': False,
            'error': reason
        }), 429  # Too Many Requests
    
    # Get user input
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({
            'success': False,
            'error': 'Missing prompt parameter'
        }), 400
    
    user_prompt = data['prompt']
    
    # STAGE 1: Sanitize input
    sanitized_input = input_sanitizer.sanitize_input(user_prompt)
    
    # STAGE 2: Validate input
    is_valid, reason = input_sanitizer.validate_input(sanitized_input)
    if not is_valid:
        log_security_event("INPUT_VALIDATION_FAILURE", sanitized_input, 
                         reason, "Request blocked", LOG_FILE)
        
        # Record suspicious activity
        threat_monitor.record_suspicious_activity(client_ip, "INVALID_INPUT", reason)
        
        return jsonify({
            'success': False,
            'error': reason
        }), 400
    
    # STAGE 3: Check for prompt injection
    is_injection, confidence, reasons = injection_detector.detect_injection(sanitized_input)
    if is_injection:
        details = f"Confidence: {confidence:.2f}, Reasons: {', '.join(reasons)}"
        log_security_event("PROMPT_INJECTION_ATTEMPT", sanitized_input, 
                         details, "Request blocked", LOG_FILE)
        
        # Record suspicious activity
        threat_monitor.record_suspicious_activity(
            client_ip, "PROMPT_INJECTION", details)
        
        return jsonify({
            'success': False,
            'error': "Potential security issue detected in your request"
        }), 400
    
    # STAGE 4: Call LLM service
    success, response = llm_service.generate_response(sanitized_input)
    
    if not success:
        return jsonify({
            'success': False,
            'error': response  # Error message
        }), 500
    
    # STAGE 5: Sanitize output
    sanitized_output = output_sanitizer.sanitize_output(response)
    
    # STAGE 6: Validate output
    is_valid, reason = output_sanitizer.validate_output(sanitized_output)
    if not is_valid:
        log_security_event("OUTPUT_VALIDATION_FAILURE", sanitized_output, 
                         reason, "Response blocked", LOG_FILE)
        
        return jsonify({
            'success': False,
            'error': "The AI generated potentially unsafe content"
        }), 500
    
    # Return the sanitized response
    return jsonify({
        'success': True,
        'response': sanitized_output
    })

@app.route('/api/health')
def health_check():
    """Check system health."""
    llm_available = llm_service.is_available()
    
    # Create empty log file if it doesn't exist
    if not os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'w') as f:
                pass
        except Exception:
            pass
    
    log_writable = os.access(LOG_FILE, os.W_OK) if os.path.exists(LOG_FILE) else False
    
    return jsonify({
        'status': 'healthy' if llm_available and log_writable else 'degraded',
        'llm_service': 'available' if llm_available else 'unavailable',
        'logging': 'writable' if log_writable else 'not writable'
    })

if __name__ == '__main__':
    # Create log file if it doesn't exist
    if not os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'w') as f:
                pass
        except Exception as e:
            print(f"Warning: Unable to create log file: {e}")
    
    app.run(debug=True)