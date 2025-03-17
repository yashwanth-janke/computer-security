# LLM Shield - Secure AI Middleware

LLM Shield is a lightweight security middleware that sits between users and Large Language Models (LLMs) like Google's Gemini. It provides protection against prompt injection attacks, input/output sanitization, and security monitoring.

## Features

- **Prompt Injection Detection**: Identifies and blocks attempts to manipulate the underlying AI system
- **Input & Output Sanitization**: Cleanses both user inputs and AI outputs for security
- **Security Monitoring**: Logs potential threats and suspicious patterns
- **Rate Limiting**: Prevents abuse through configurable rate limits
- **Simple API**: Easy integration with various LLM providers
- **Clean UI**: Simple web interface for interacting with the protected AI

## Project Structure

```
llm_shield/
│
├── app.py               # Main Flask application
├── config.py            # Configuration settings
├── requirements.txt     # Project dependencies
│
├── security/
│   ├── input_sanitizer.py    # User input sanitization
│   ├── output_sanitizer.py   # AI output sanitization
│   ├── prompt_injection.py   # Prompt injection detection
│   ├── threat_monitor.py     # Security monitoring & logging
│   └── security_utils.py     # Shared security utilities
│
├── services/
│   └── llm_service.py        # Integration with Gemini API
│
├── static/              # Frontend assets
│   ├── css/
│   └── js/
│
├── templates/           # HTML templates
│
└── README.md            # Documentation
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Google API key with access to Gemini

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/llm-shield.git
   cd llm-shield
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the root directory with your API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   GEMINI_MODEL=gemini-pro
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Open your browser and navigate to `http://localhost:5000`

## Security Features

### Input Sanitization

- Removes HTML/JavaScript to prevent XSS attacks
- Validates input length and content against security rules
- Blocks inputs containing sensitive topics or harmful patterns

### Prompt Injection Detection

- Analyzes input for command words that may attempt to manipulate the AI
- Detects delimiter patterns that could signal system prompt formatting
- Identifies impersonation attempts of system or privileged modes

### Output Sanitization

- Strips HTML and potentially harmful content from AI responses
- Redacts potential PII (Personally Identifiable Information)
- Validates AI outputs against security constraints

### Threat Monitoring

- Implements rate limiting to prevent abuse
- Records and analyzes suspicious activity patterns
- Logs security events for audit and analysis

## API Usage

Send a POST request to `/api/chat` with the following JSON payload:

```json
{
  "prompt": "Your message to the AI here"
}
```

Success response:

```json
{
  "success": true,
  "response": "AI's sanitized response"
}
```

Error response:

```json
{
  "success": false,
  "error": "Error message explaining what went wrong"
}
```

## Security Logs

View security logs at `/logs` in the web interface. These logs track security events such as:

- Prompt injection attempts
- Rate limit violations
- Input/output validation failures
- Suspicious activity patterns

## Configuration

Edit `config.py` to adjust:

- Security settings
- Blocked patterns
- Rate limiting parameters
- LLM API configuration

## License

[MIT License](LICENSE)

## Disclaimer

This is a security middleware intended to reduce risks when interacting with LLMs. While it implements multiple layers of protection, no security solution is perfect. Always practice defense in depth and maintain proper security practices.