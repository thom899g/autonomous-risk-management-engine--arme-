"""
Firebase State Manager
Centralized Firebase client for real-time state management and data streaming
"""
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

# Conditional import with fallback
try:
    import firebase_admin
    from firebase_admin import credentials, db, firestore
    from firebase_admin.exceptions import FirebaseError
    FIREBASE_AVAILABLE = True
except ImportError:
    logging.warning("firebase-admin not installed. Using mock for development.")
    FIREBASE_AVAILABLE = False

from config import get_config

class FirebaseStateManager:
    """Firebase client for real-time state management with fallback caching"""
    
    def __init__(self):
        self.config = get_config()
        self.client = None
        self.realtime_db = None
        self.firestore_db = None
        self._initialized = False
        self._cache = {}  # Local cache for fallback
        
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize Firebase connection with error handling"""
        if not FIREBASE_AVAILABLE:
            logging.warning("Running in mock mode - no Firebase connection")
            return
            
        try:
            # Check if Firebase app already exists
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.config.firebase_credentials_path)
                firebase_admin.initialize_app(cred,