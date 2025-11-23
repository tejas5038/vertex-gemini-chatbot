"""
Flask application for Vertex AI Gemini chatbot with memory and tools.
"""

import os
import logging
from flask import Flask, render_template, request, jsonify
from shared.utils import (
    init_gemini, 
    get_model_name, 
    get_firestore_collection,
    format_error_response
)
from shared.decorators import handle_errors, validate_json, log_request
from shared.validators import validate_session_id, validate_user_message
from shared.tools import get_tool_functions, execute_tool
from shared.memory_store import FirestoreMemoryStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Gemini client and memory store
try:
    gemini_client = init_gemini()
    model_name = get_model_name()
    memory_store = FirestoreMemoryStore(get_firestore_collection())
    logger.info(f"Application initialized with model: {model_name}")
except Exception as e:
    logger.error(f"Failed to initialize application: {str(e)}")
    raise

# System prompt with tool instructions
SYSTEM_PROMPT = """You are a helpful AI assistant with access to tools. You can:

1. **Calculate** mathematical expressions using the calculator tool
2. **Fetch data** from whitelisted public APIs using the fetch_url tool
3. **Draft emails** using the send_email tool (note: actual sending requires configuration)

When a user asks you to perform these tasks, use the appropriate tool. Always explain what you're doing and provide clear results.

For mathematical calculations, use the calculator tool with valid expressions.
For fetching web data, use the fetch_url tool with complete URLs.
For emails, use the send_email tool but inform users it's currently a stub.

Be concise, helpful, and accurate. If a tool fails, explain why and suggest alternatives."""


def build_gemini_contents(history: list, user_message: str) -> list:
    """
    Build contents array for Gemini API from history and new message.
    
    Args:
        history: List of previous messages
        user_message: New user message
        
    Returns:
        List of content dictionaries
    """
    contents = []
    
    # Add conversation history
    for msg in history:
        contents.append({
            'role': msg['role'],
            'parts': [{'text': msg['content']}]
        })
    
    # Add new user message
    contents.append({
        'role': 'user',
        'parts': [{'text': user_message}]
    })
    
    return contents


def process_with_tools(session_id: str, user_message: str) -> dict:
    """
    Process user message with Gemini, handling tool calls.
    
    Args:
        session_id: Session identifier
        user_message: User's message
        
    Returns:
        Dict with assistant response and metadata
    """
    # Get conversation history
    history = memory_store.get_history(session_id)
    
    # Build contents for Gemini
    contents = build_gemini_contents(history, user_message)
    
    # Prepare tool configurations
    tools = get_tool_functions()
    
    try:
        # Initial call to Gemini
        response = gemini_client.models.generate_content(
            model=model_name,
            contents=contents,
            config={
                'system_instruction': SYSTEM_PROMPT,
                'tools': tools,
                'temperature': 0.7,
            }
        )
        
        tool_calls_made = []
        max_iterations = 5  # Prevent infinite loops
        iteration = 0
        
        # Tool calling loop
        while iteration < max_iterations:
            candidate = response.candidates[0] if response.candidates else None
            if not candidate:
                break
            
            # Check for function calls
            if hasattr(candidate.content, 'parts'):
                function_calls = [
                    part for part in candidate.content.parts 
                    if hasattr(part, 'function_call') and part.function_call is not None
                ]
                
                if not function_calls:
                    # No more tool calls, we have final answer
                    break
                
                # Execute each function call
                for fc_part in function_calls:
                    func_call = fc_part.function_call
                    
                    # Additional safety check
                    if func_call is None or not hasattr(func_call, 'name'):
                        logger.warning(f"Skipping invalid function call: {fc_part}")
                        continue
                    
                    tool_name = func_call.name
                    parameters = dict(func_call.args) if hasattr(func_call, 'args') else {}
                    
                    logger.info(f"Executing tool: {tool_name} with params: {parameters}")
                    
                    # Execute the tool
                    result = execute_tool(tool_name, parameters)
                    tool_calls_made.append({
                        'tool': tool_name,
                        'parameters': parameters,
                        'result': result
                    })
                    
                    # Add function response to contents
                    contents.append({
                        'role': 'model',
                        'parts': [fc_part]
                    })
                    contents.append({
                        'role': 'user',
                        'parts': [{
                            'function_response': {
                                'name': tool_name,
                                'response': result
                            }
                        }]
                    })
                
                # Continue conversation with tool results
                response = gemini_client.models.generate_content(
                    model=model_name,
                    contents=contents,
                    config={
                        'system_instruction': SYSTEM_PROMPT,
                        'tools': tools,
                        'temperature': 0.7,
                    }
                )
                iteration += 1
            else:
                break
        
        # Extract final text response
        final_text = ""
        if response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate.content, 'parts'):
                text_parts = [
                    part.text for part in candidate.content.parts 
                    if hasattr(part, 'text')
                ]
                final_text = ''.join(text_parts)
        
        if not final_text:
            final_text = "I apologize, but I couldn't generate a proper response. Please try again."
        
        # Save to memory
        memory_store.append_turn(session_id, 'user', user_message)
        memory_store.append_turn(session_id, 'model', final_text)
        
        return {
            'assistant_message': final_text,
            'tool_calls': tool_calls_made if tool_calls_made else None,
            'usage': {
                'iterations': iteration,
                'tools_used': len(tool_calls_made)
            }
        }
    
    except Exception as e:
        logger.error(f"Error in process_with_tools: {str(e)}", exc_info=True)
        raise


@app.route('/')
def index():
    """Render the main chat interface."""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
@log_request
@validate_json
@handle_errors
def chat():
    """
    Handle chat messages.
    
    Expected JSON:
        {
            "session_id": "unique-session-id",
            "user_message": "Hello, can you help me?"
        }
    
    Returns:
        JSON response with assistant message
    """
    data = request.get_json()
    
    # Validate inputs
    session_id = data.get('session_id', '')
    user_message = data.get('user_message', '')
    
    validate_session_id(session_id)
    validate_user_message(user_message)
    
    # Process with Gemini
    result = process_with_tools(session_id, user_message.strip())
    
    return jsonify({
        'error': False,
        **result
    })


@app.route('/api/reset', methods=['POST'])
@log_request
@validate_json
@handle_errors
def reset():
    """
    Reset conversation history for a session.
    
    Expected JSON:
        {
            "session_id": "unique-session-id"
        }
    
    Returns:
        JSON response confirming reset
    """
    data = request.get_json()
    session_id = data.get('session_id', '')
    
    validate_session_id(session_id)
    
    success = memory_store.clear(session_id)
    
    if success:
        return jsonify({
            'error': False,
            'message': 'Conversation history cleared successfully'
        })
    else:
        return jsonify({
            'error': True,
            'message': 'Failed to clear conversation history'
        }), 500


@app.route('/health')
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'model': model_name,
        'sessions': memory_store.get_session_count()
    })


if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)