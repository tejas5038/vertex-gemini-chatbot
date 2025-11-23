"""
Utility functions for initializing Gemini client and other helpers.
"""

import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_gemini():
    """
    Initialize and return Google Gemini client configured for Vertex AI.
    
    Returns:
        genai.Client: Configured Gemini client
    """
    project_id = os.getenv('GCP_PROJECT_ID')
    location = os.getenv('GCP_LOCATION', 'us-central1')
    
    if not project_id:
        raise ValueError("GCP_PROJECT_ID environment variable is required")
    
    # Initialize client with Vertex AI
    client = genai.Client(
        vertexai=True,
        project=project_id,
        location=location
    )
    
    return client


def get_model_name():
    """
    Get the Gemini model name from environment variables.
    
    Returns:
        str: Model name
    """
    return os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-exp')


def get_firestore_collection():
    """
    Get the Firestore collection name from environment variables.
    
    Returns:
        str: Collection name
    """
    return os.getenv('FIRESTORE_COLLECTION', 'chat_sessions')


def format_error_response(error_message: str, status_code: int = 500):
    """
    Format a standardized error response.
    
    Args:
        error_message: The error message
        status_code: HTTP status code
        
    Returns:
        tuple: (response_dict, status_code)
    """
    return {
        'error': True,
        'message': error_message,
        'assistant_message': None
    }, status_code
