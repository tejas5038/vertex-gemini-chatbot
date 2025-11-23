"""
Firestore-based conversation memory storage.
"""

import logging
from typing import List, Dict, Any
from google.cloud import firestore
from datetime import datetime

logger = logging.getLogger(__name__)


class FirestoreMemoryStore:
    """
    Manages conversation history in Firestore.
    """
    
    def __init__(self, collection_name: str):
        """
        Initialize Firestore memory store.
        
        Args:
            collection_name: Firestore collection name
        """
        self.db = firestore.Client()
        self.collection_name = collection_name
        self.collection = self.db.collection(collection_name)
        logger.info(f"Initialized FirestoreMemoryStore with collection: {collection_name}")
    
    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        try:
            doc_ref = self.collection.document(session_id)
            doc = doc_ref.get()
            
            if doc.exists:
                data = doc.to_dict()
                return data.get('messages', [])
            else:
                logger.info(f"No history found for session: {session_id}")
                return []
        except Exception as e:
            logger.error(f"Error retrieving history for {session_id}: {str(e)}")
            return []
    
    def append_turn(self, session_id: str, role: str, content: str) -> bool:
        """
        Append a message to conversation history.
        
        Args:
            session_id: Session identifier
            role: Message role ('user' or 'model')
            content: Message content
            
        Returns:
            bool: True if successful
        """
        try:
            doc_ref = self.collection.document(session_id)
            
            message = {
                'role': role,
                'content': content,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Get existing document or create new
            doc = doc_ref.get()
            
            if doc.exists:
                # Append to existing messages
                doc_ref.update({
                    'messages': firestore.ArrayUnion([message]),
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
            else:
                # Create new document
                doc_ref.set({
                    'session_id': session_id,
                    'messages': [message],
                    'created_at': firestore.SERVER_TIMESTAMP,
                    'updated_at': firestore.SERVER_TIMESTAMP
                })
            
            logger.info(f"Appended {role} message to session {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error appending turn for {session_id}: {str(e)}")
            return False
    
    def clear(self, session_id: str) -> bool:
        """
        Clear conversation history for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if successful
        """
        try:
            doc_ref = self.collection.document(session_id)
            doc_ref.delete()
            logger.info(f"Cleared history for session: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing history for {session_id}: {str(e)}")
            return False
    
    def get_session_count(self) -> int:
        """
        Get total number of sessions.
        
        Returns:
            int: Number of sessions
        """
        try:
            docs = self.collection.stream()
            return sum(1 for _ in docs)
        except Exception as e:
            logger.error(f"Error getting session count: {str(e)}")
            return 0
