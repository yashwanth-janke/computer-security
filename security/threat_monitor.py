import json
import time
from datetime import datetime, timedelta
from config import LOG_FILE

class ThreatMonitor:
    """
    Monitors and logs potential security threats, implementing rate limiting
    and pattern detection across multiple requests.
    """
    
    def __init__(self):
        self.request_history = {}  # IP address -> list of request timestamps
        self.blocked_ips = {}      # IP address -> unblock time
        self.suspicious_activity = {}  # IP address -> count of suspicious requests
        
        # Rate limiting settings
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max_requests = 20  # max requests per window
        self.suspicious_threshold = 3  # number of suspicious requests before temporary block
        self.block_duration = 300  # seconds (5 minutes)
    
    def check_rate_limit(self, ip_address):
        """
        Check if an IP address has exceeded the rate limit.
        
        Args:
            ip_address (str): Client IP address
            
        Returns:
            tuple: (is_allowed, reason)
        """
        current_time = time.time()
        
        # Check if IP is currently blocked
        if ip_address in self.blocked_ips:
            if current_time < self.blocked_ips[ip_address]:
                remaining = int(self.blocked_ips[ip_address] - current_time)
                return False, f"IP address temporarily blocked. Try again in {remaining} seconds."
            else:
                # Unblock IP if block duration has passed
                del self.blocked_ips[ip_address]
        
        # Initialize request history for new IPs
        if ip_address not in self.request_history:
            self.request_history[ip_address] = []
        
        # Clean up old requests outside the window
        self.request_history[ip_address] = [
            timestamp for timestamp in self.request_history[ip_address]
            if current_time - timestamp <= self.rate_limit_window
        ]
        
        # Check if rate limit is exceeded
        if len(self.request_history[ip_address]) >= self.rate_limit_max_requests:
            # Block the IP
            self.blocked_ips[ip_address] = current_time + self.block_duration
            self.log_threat("RATE_LIMIT_EXCEEDED", ip_address, 
                           f"Made {len(self.request_history[ip_address])} requests in {self.rate_limit_window}s",
                           "Temporary block applied")
            return False, f"Rate limit exceeded. Try again in {self.block_duration} seconds."
        
        # Add current request to history
        self.request_history[ip_address].append(current_time)
        return True, "Request allowed"
    
    def log_threat(self, threat_type, source, details, action_taken):
        """
        Log a security threat to the log file.
        
        Args:
            threat_type (str): Type of threat detected
            source (str): Source of the threat (e.g., IP address)
            details (str): Details about the threat
            action_taken (str): Action taken in response
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "threat_type": threat_type,
            "source": source,
            "details": details,
            "action_taken": action_taken
        }
        
        try:
            with open(LOG_FILE, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            print(f"Error logging threat: {e}")
    
    def record_suspicious_activity(self, ip_address, activity_type, details):
        """
        Record suspicious activity and potentially block IP.
        
        Args:
            ip_address (str): Client IP address
            activity_type (str): Type of suspicious activity
            details (str): Details about the activity
            
        Returns:
            bool: True if IP is now blocked, False otherwise
        """
        if ip_address not in self.suspicious_activity:
            self.suspicious_activity[ip_address] = 0
            
        self.suspicious_activity[ip_address] += 1
        
        # Log the suspicious activity
        self.log_threat(activity_type, ip_address, details, 
                       "Monitoring" if self.suspicious_activity[ip_address] < self.suspicious_threshold 
                       else "Temporary block applied")
        
        # Block IP if threshold is reached
        if self.suspicious_activity[ip_address] >= self.suspicious_threshold:
            current_time = time.time()
            self.blocked_ips[ip_address] = current_time + self.block_duration
            return True
            
        return False
    
    def get_recent_threats(self, limit=50):
        """
        Get the most recent security threats from the log file.
        
        Args:
            limit (int): Maximum number of threats to return
            
        Returns:
            list: List of threat log entries
        """
        threats = []
        try:
            with open(LOG_FILE, 'r') as f:
                for line in f:
                    try:
                        threat = json.loads(line.strip())
                        threats.append(threat)
                    except json.JSONDecodeError:
                        continue
        except FileNotFoundError:
            return []
        
        # Sort by timestamp (newest first) and limit
        return sorted(threats, key=lambda x: x.get('timestamp', ''), reverse=True)[:limit]