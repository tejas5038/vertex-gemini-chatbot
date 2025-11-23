"""
Tool definitions and execution for Gemini function calling.
"""

import json
import logging
from typing import Dict, Any, List
import requests
from .validators import validate_math_expression, validate_url

logger = logging.getLogger(__name__)

# Whitelisted domains for web fetch tool
# Cloud Shell compatible APIs
ALLOWED_DOMAINS = [
    # Google APIs (work in Cloud Shell)
    'storage.googleapis.com',
    'www.googleapis.com',
    'cloudresourcemanager.googleapis.com',
    
    # Public testing APIs that work
    'httpbin.org',
    'postman-echo.com',
    'api.ipify.org',
    'ifconfig.me',
    
    # May work (test these)
    'jsonplaceholder.typicode.com',
    'api.github.com',
    'dog.ceo',
    'catfact.ninja',
    'official-joke-api.appspot.com',
    'api.chucknorris.io',
    'api.quotable.io',
    
    # Original list (may be blocked)
    'api.coindesk.com',
    'api.openweathermap.org',
    'api.exchangerate-api.com',
    'restcountries.com',
]


# ============================================================================
# Tool Implementation Functions (Internal)
# ============================================================================

def _execute_calculator_impl(expression: str) -> Dict[str, Any]:
    """
    Internal: Safely evaluate a mathematical expression.
    """
    try:
        validate_math_expression(expression)
        result = eval(expression, {"__builtins__": {}}, {})
        return {
            "success": True,
            "result": result,
            "expression": expression
        }
    except Exception as e:
        logger.error(f"Calculator error: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to evaluate expression: {str(e)}",
            "expression": expression
        }


def _execute_fetch_url_impl(url: str) -> Dict[str, Any]:
    """
    Internal: Fetch data from a whitelisted URL.
    """
    try:
        validate_url(url, ALLOWED_DOMAINS)
        response = requests.get(url, timeout=10, headers={
            'User-Agent': 'VertexGeminiChatbot/1.0'
        })
        response.raise_for_status()
        
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = response.text
        
        return {
            "success": True,
            "url": url,
            "status_code": response.status_code,
            "data": data
        }
    except Exception as e:
        logger.error(f"Fetch URL error: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to fetch URL: {str(e)}",
            "url": url
        }


def _execute_send_email_impl(to: str, subject: str, body: str) -> Dict[str, Any]:
    """
    Send email via SendGrid API.
    """
    import os
    
    api_key = os.getenv('SENDGRID_API_KEY')
    
    # Check if SendGrid is configured
    if not api_key:
        logger.info(f"Email tool called (stub): to={to}, subject={subject}")
        return {
            "success": False,
            "stub": True,
            "message": "Email tool is not configured. SendGrid API key not found.",
            "details": {
                "to": to,
                "subject": subject,
                "body_preview": body[:100] + "..." if len(body) > 100 else body
            },
            "instructions": (
                "To enable email sending:\n"
                "1. Sign up at https://signup.sendgrid.com/\n"
                "2. Create an API key\n"
                "3. Add SENDGRID_API_KEY to your .env file\n"
                "4. Verify a sender email in SendGrid dashboard"
            )
        }
    
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail
        
        # Get verified sender email from env or use default
        from_email = os.getenv('SENDGRID_FROM_EMAIL', 'TEJAS5038@GMAIL.COM')
        
        message = Mail(
            from_email=from_email,
            to_emails=to,
            subject=subject,
            html_content=f'<p>{body}</p>'
        )
        
        sg = SendGridAPIClient(api_key)
        response = sg.send(message)
        
        logger.info(f"Email sent successfully to {to}")
        
        return {
            "success": True,
            "message": f"Email sent successfully to {to}",
            "status_code": response.status_code,
            "details": {
                "to": to,
                "subject": subject,
                "from": from_email
            }
        }
        
    except Exception as e:
        logger.error(f"SendGrid error: {str(e)}")
        return {
            "success": False,
            "error": f"Failed to send email: {str(e)}",
            "details": {
                "to": to,
                "subject": subject
            }
        }


# ============================================================================
# Tool Functions for Gemini (Must be top-level callables with docstrings)
# ============================================================================

def calculator(expression: str) -> Dict[str, Any]:
    """
    Evaluates mathematical expressions safely. Supports +, -, *, /, parentheses, and decimal numbers.
    
    Args:
        expression: A mathematical expression to evaluate (e.g., '25 * 47 + 100')
        
    Returns:
        Dict with calculation result
    """
    return _execute_calculator_impl(expression)


def fetch_url(url: str) -> Dict[str, Any]:
    """
    Fetches data from whitelisted public APIs. Returns JSON response.
    
    Args:
        url: The complete URL to fetch (must be from whitelisted domains)
        
    Returns:
        Dict with fetched data
    """
    return _execute_fetch_url_impl(url)


def send_email(to: str, subject: str, body: str) -> Dict[str, Any]:
    """
    Sends an email via Gmail API (currently a stub - requires OAuth setup).
    
    Args:
        to: Recipient email address
        subject: Email subject line
        body: Email body content
        
    Returns:
        Dict with send status
    """
    return _execute_send_email_impl(to, subject, body)


# ============================================================================
# Tool Registry
# ============================================================================

def get_tool_functions() -> List:
    """
    Return list of tool functions for Gemini.
    These must be actual Python callables with proper docstrings.
    
    Returns:
        List of callable tool functions
    """
    return [calculator, fetch_url, send_email]


def execute_tool(tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool by name with given parameters.
    
    Args:
        tool_name: Name of the tool to execute
        parameters: Parameters for the tool
        
    Returns:
        Dict with tool execution result
    """
    tool_map = {
        'calculator': calculator,
        'fetch_url': fetch_url,
        'send_email': send_email
    }
    
    if tool_name not in tool_map:
        return {
            "success": False,
            "error": f"Unknown tool: {tool_name}"
        }
    
    try:
        tool_func = tool_map[tool_name]
        return tool_func(**parameters)
    except Exception as e:
        logger.error(f"Tool execution error for {tool_name}: {str(e)}")
        return {
            "success": False,
            "error": f"Tool execution failed: {str(e)}"
        }