"""
Input validation functions.
"""

import re


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.
    
    Args:
        session_id: Session identifier
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If invalid
    """
    if not session_id or not isinstance(session_id, str):
        raise ValueError("session_id must be a non-empty string")
    
    if len(session_id) > 100:
        raise ValueError("session_id must be 100 characters or less")
    
    # Only allow alphanumeric, hyphens, underscores
    if not re.match(r'^[a-zA-Z0-9_-]+$', session_id):
        raise ValueError("session_id contains invalid characters")
    
    return True


def validate_user_message(message: str) -> bool:
    """
    Validate user message.
    
    Args:
        message: User's message
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If invalid
    """
    if not message or not isinstance(message, str):
        raise ValueError("user_message must be a non-empty string")
    
    message = message.strip()
    
    if len(message) == 0:
        raise ValueError("user_message cannot be empty or only whitespace")
    
    if len(message) > 10000:
        raise ValueError("user_message must be 10,000 characters or less")
    
    return True


def validate_math_expression(expression: str) -> bool:
    """
    Validate that expression contains only safe mathematical operations.
    
    Args:
        expression: Mathematical expression
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If invalid or unsafe
    """
    if not expression or not isinstance(expression, str):
        raise ValueError("Expression must be a non-empty string")
    
    # Only allow numbers, operators, parentheses, decimal points, and spaces
    safe_pattern = r'^[\d\+\-\*/\(\)\.\s]+$'
    
    if not re.match(safe_pattern, expression):
        raise ValueError("Expression contains invalid characters")
    
    # Prevent common attack vectors
    dangerous_patterns = [
        '__', 'import', 'exec', 'eval', 'compile', 
        'open', 'file', 'input', 'raw_input'
    ]
    
    expression_lower = expression.lower()
    for pattern in dangerous_patterns:
        if pattern in expression_lower:
            raise ValueError(f"Expression contains forbidden pattern: {pattern}")
    
    return True


def validate_url(url: str, whitelist: list) -> bool:
    """
    Validate URL against whitelist.
    
    Args:
        url: URL to validate
        whitelist: List of allowed domains
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If invalid or not whitelisted
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    if not url.startswith(('http://', 'https://')):
        raise ValueError("URL must start with http:// or https://")
    
    # Extract domain
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check whitelist
        if not any(domain == allowed or domain.endswith('.' + allowed) 
                   for allowed in whitelist):
            raise ValueError(f"Domain {domain} is not in whitelist")
        
        return True
    except Exception as e:
        raise ValueError(f"Invalid URL format: {str(e)}")
