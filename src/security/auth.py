"""
API Authentication - Phase 6
Simple API key authentication for production
"""
import secrets
import hashlib
from typing import Optional, Dict
import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class APIKeyAuth:
    """
    API Key Authentication
    - Generate and manage API keys
    - Validate requests
    - Track usage
    """
    
    def __init__(self, db_path: str = "chainpilot.db"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        logger.info("API Key Auth initialized")
    
    async def connect(self):
        """Initialize database"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_hash TEXT UNIQUE NOT NULL,
                key_prefix TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL,
                last_used TEXT,
                is_active BOOLEAN DEFAULT 1,
                permissions TEXT DEFAULT 'read,write'
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key_prefix TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ip_address TEXT
            )
        """)
        
        self.conn.commit()
        logger.info("API Key Auth database initialized")
    
    async def disconnect(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def generate_api_key(self, name: str) -> str:
        """
        Generate a new API key
        
        Returns:
            The API key (only shown once!)
        """
        # Generate secure random key
        api_key = f"cp_{secrets.token_urlsafe(32)}"
        
        # Hash the key for storage
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        key_prefix = api_key[:10]  # Store prefix for identification
        
        timestamp = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_keys (key_hash, key_prefix, name, created_at)
                VALUES (?, ?, ?, ?)
            """, (key_hash, key_prefix, name, timestamp))
            conn.commit()
        
        logger.info(f"Generated API key for: {name}")
        return api_key
    
    def validate_api_key(self, api_key: str) -> bool:
        """
        Validate an API key
        
        Returns:
            True if valid and active
        """
        if not api_key or not api_key.startswith("cp_"):
            return False
        
        # Hash the provided key
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM api_keys WHERE key_hash = ? AND is_active = 1
            """, (key_hash,))
            
            result = cursor.fetchone()
            
            if result:
                # Update last used
                cursor.execute("""
                    UPDATE api_keys SET last_used = ? WHERE key_hash = ?
                """, (datetime.utcnow().isoformat(), key_hash))
                conn.commit()
                
                logger.debug(f"Valid API key: {result['key_prefix']}")
                return True
        
        logger.warning(f"Invalid API key attempted")
        return False
    
    def record_usage(self, api_key: str, endpoint: str, ip_address: str):
        """Record API usage"""
        if api_key.startswith("cp_"):
            key_prefix = api_key[:10]
            timestamp = datetime.utcnow().isoformat()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO api_usage (key_prefix, endpoint, timestamp, ip_address)
                    VALUES (?, ?, ?, ?)
                """, (key_prefix, endpoint, timestamp, ip_address))
                conn.commit()
    
    def list_api_keys(self) -> list:
        """List all API keys (without revealing the actual keys)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT key_prefix, name, created_at, last_used, is_active FROM api_keys ORDER BY created_at DESC")
            return [dict(row) for row in cursor.fetchall()]
    
    def revoke_api_key(self, key_prefix: str) -> bool:
        """Revoke an API key"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE api_keys SET is_active = 0 WHERE key_prefix = ?
            """, (key_prefix,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Revoked API key: {key_prefix}")
                return True
        return False


# Global auth instance
api_auth = APIKeyAuth()

