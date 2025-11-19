"""
Audit Logger - Database logging for all transactions and events
"""
import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Logs all transactions and events to SQLite database
    Provides complete audit trail for compliance
    """
    
    def __init__(self, db_path: str = "./chainpilot.db"):
        """
        Initialize audit logger
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_database()
        logger.info(f"Audit logger initialized: {db_path}")
    
    def _init_database(self):
        """Create database tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Transactions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_hash TEXT UNIQUE,
                    from_address TEXT NOT NULL,
                    to_address TEXT NOT NULL,
                    value TEXT NOT NULL,
                    gas_limit INTEGER,
                    gas_price TEXT,
                    gas_used INTEGER,
                    status TEXT NOT NULL,
                    token_address TEXT,
                    token_symbol TEXT,
                    block_number INTEGER,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    error TEXT
                )
            """)
            
            # Indexes for transactions
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_from_address 
                ON transactions(from_address)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tx_hash 
                ON transactions(tx_hash)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status 
                ON transactions(status)
            """)
            
            # Events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_event_type 
                ON events(event_type)
            """)
            
            conn.commit()
            logger.info("Database tables initialized")
    
    def log_transaction(
        self,
        tx_hash: str,
        from_address: str,
        to_address: str,
        value: str,
        status: str,
        gas_limit: Optional[int] = None,
        gas_price: Optional[str] = None,
        gas_used: Optional[int] = None,
        token_address: Optional[str] = None,
        token_symbol: Optional[str] = None,
        block_number: Optional[int] = None,
        error: Optional[str] = None
    ) -> int:
        """
        Log a transaction to database
        
        Args:
            tx_hash: Transaction hash
            from_address: Sender address
            to_address: Recipient address
            value: Amount in wei (string)
            status: PENDING, SUBMITTED, CONFIRMED, FAILED
            gas_limit: Gas limit
            gas_price: Gas price in wei
            gas_used: Actual gas used
            token_address: Token contract address (None for native)
            token_symbol: Token symbol
            block_number: Block number when confirmed
            error: Error message if failed
            
        Returns:
            int: Database row ID
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if transaction exists (for updates)
            cursor.execute(
                "SELECT id FROM transactions WHERE tx_hash = ?",
                (tx_hash,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Update existing transaction
                cursor.execute("""
                    UPDATE transactions
                    SET status = ?, gas_used = ?, block_number = ?, error = ?
                    WHERE tx_hash = ?
                """, (status, gas_used, block_number, error, tx_hash))
                row_id = existing[0]
                logger.info(f"Updated transaction {tx_hash}: {status}")
            else:
                # Insert new transaction
                cursor.execute("""
                    INSERT INTO transactions (
                        tx_hash, from_address, to_address, value,
                        gas_limit, gas_price, gas_used, status,
                        token_address, token_symbol, block_number, error
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    tx_hash, from_address, to_address, value,
                    gas_limit, gas_price, gas_used, status,
                    token_address, token_symbol, block_number, error
                ))
                row_id = cursor.lastrowid
                logger.info(f"Logged new transaction {tx_hash}: {status}")
            
            conn.commit()
            return row_id
    
    def log_event(self, event_type: str, data: Dict[str, Any]):
        """
        Log an event
        
        Args:
            event_type: Type of event (e.g., WALLET_CREATED, TX_SENT)
            data: Event data (will be JSON serialized)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (event_type, data)
                VALUES (?, ?)
            """, (event_type, json.dumps(data)))
            conn.commit()
            logger.debug(f"Logged event: {event_type}")
    
    def get_transaction(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get transaction by hash
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            dict: Transaction data or None
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM transactions WHERE tx_hash = ?
            """, (tx_hash,))
            row = cursor.fetchone()
            
            if row:
                return dict(row)
            return None
    
    def get_transaction_history(
        self,
        from_address: Optional[str] = None,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get transaction history
        
        Args:
            from_address: Filter by sender address
            limit: Maximum number of transactions
            status: Filter by status
            
        Returns:
            list: List of transaction dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM transactions WHERE 1=1"
            params = []
            
            if from_address:
                query += " AND from_address = ?"
                params.append(from_address)
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
    
    def get_pending_transactions(self) -> List[Dict[str, Any]]:
        """Get all pending/submitted transactions"""
        return self.get_transaction_history(
            status="SUBMITTED",
            limit=100
        )
    
    def get_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get events
        
        Args:
            event_type: Filter by event type
            limit: Maximum number of events
            
        Returns:
            list: List of event dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if event_type:
                cursor.execute("""
                    SELECT * FROM events
                    WHERE event_type = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (event_type, limit))
            else:
                cursor.execute("""
                    SELECT * FROM events
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (limit,))
            
            rows = cursor.fetchall()
            events = []
            
            for row in rows:
                event = dict(row)
                # Parse JSON data
                if event['data']:
                    try:
                        event['data'] = json.loads(event['data'])
                    except json.JSONDecodeError:
                        pass
                events.append(event)
            
            return events
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get transaction statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Total transactions
            cursor.execute("SELECT COUNT(*) FROM transactions")
            total = cursor.fetchone()[0]
            
            # By status
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM transactions
                GROUP BY status
            """)
            by_status = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Total value transferred (native only)
            cursor.execute("""
                SELECT SUM(CAST(value AS REAL))
                FROM transactions
                WHERE token_address IS NULL AND status = 'CONFIRMED'
            """)
            total_value = cursor.fetchone()[0] or 0
            
            return {
                "total_transactions": total,
                "by_status": by_status,
                "total_value_transferred_wei": str(int(total_value))
            }

