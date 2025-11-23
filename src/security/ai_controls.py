"""
AI Spending Controls - Phase 6
Enhanced security controls for AI-initiated transactions
"""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import sqlite3
from enum import Enum

logger = logging.getLogger(__name__)


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class AISecurityLevel(str, Enum):
    """Security levels for AI actions"""
    UNRESTRICTED = "unrestricted"  # No limits (dangerous!)
    MODERATE = "moderate"          # Some limits
    STRICT = "strict"              # Strong limits (recommended)
    LOCKDOWN = "lockdown"          # Requires approval for everything


class AISpendingController:
    """
    Controls AI spending with multi-layer security:
    1. Transaction amount limits
    2. Daily/hourly spending caps
    3. Approval requirements for large amounts
    4. Transaction frequency limits
    5. Suspicious activity detection
    """
    
    def __init__(self, db_path: str = "chainpilot.db", security_level: AISecurityLevel = AISecurityLevel.STRICT):
        self.db_path = db_path
        self.security_level = security_level
        self.conn: Optional[sqlite3.Connection] = None
        
        # Security thresholds based on level
        self.thresholds = self._get_thresholds(security_level)
        
        logger.info(f"AI Spending Controller initialized with {security_level.value} security")
    
    def _get_thresholds(self, level: AISecurityLevel) -> Dict[str, Any]:
        """Get security thresholds based on security level"""
        thresholds = {
            AISecurityLevel.UNRESTRICTED: {
                "max_single_tx": float('inf'),
                "hourly_limit": float('inf'),
                "daily_limit": float('inf'),
                "approval_threshold": float('inf'),
                "max_tx_per_hour": 1000,
                "require_approval": False
            },
            AISecurityLevel.MODERATE: {
                "max_single_tx": 1.0,  # 1 ETH per transaction
                "hourly_limit": 5.0,    # 5 ETH per hour
                "daily_limit": 20.0,    # 20 ETH per day
                "approval_threshold": 0.5,  # Require approval > 0.5 ETH
                "max_tx_per_hour": 50,
                "require_approval": False
            },
            AISecurityLevel.STRICT: {
                "max_single_tx": 0.5,   # 0.5 ETH per transaction
                "hourly_limit": 2.0,     # 2 ETH per hour
                "daily_limit": 10.0,     # 10 ETH per day
                "approval_threshold": 0.1,  # Require approval > 0.1 ETH
                "max_tx_per_hour": 20,
                "require_approval": False
            },
            AISecurityLevel.LOCKDOWN: {
                "max_single_tx": 0.1,    # 0.1 ETH per transaction
                "hourly_limit": 0.5,     # 0.5 ETH per hour
                "daily_limit": 2.0,      # 2 ETH per day
                "approval_threshold": 0.01,  # Require approval > 0.01 ETH
                "max_tx_per_hour": 5,
                "require_approval": True  # Require approval for ALL transactions
            }
        }
        return thresholds[level]
    
    async def connect(self):
        """Connect to database and create tables"""
        self.conn = sqlite3.connect(self.db_path)
        cursor = self.conn.cursor()
        
        # Create AI spending history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_spending_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                from_address TEXT NOT NULL,
                to_address TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                approved BOOLEAN NOT NULL,
                approval_id TEXT,
                notes TEXT
            )
        """)
        
        # Create approval requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS approval_requests (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                from_address TEXT NOT NULL,
                to_address TEXT NOT NULL,
                amount REAL NOT NULL,
                currency TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL,
                approved_at TEXT,
                approved_by TEXT
            )
        """)
        
        self.conn.commit()
        logger.info("AI spending control database initialized")
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    async def check_ai_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        currency: str = "ETH"
    ) -> Dict[str, Any]:
        """
        Check if AI can execute this transaction
        
        Returns:
            Dict with:
                - allowed: bool
                - reason: str
                - requires_approval: bool
                - approval_id: Optional[str]
                - limits_info: Dict
        """
        # Get spending history
        hourly_spent = await self._get_spending(hours=1)
        daily_spent = await self._get_spending(hours=24)
        hourly_tx_count = await self._get_transaction_count(hours=1)
        
        limits_info = {
            "hourly_spent": hourly_spent,
            "daily_spent": daily_spent,
            "hourly_limit": self.thresholds["hourly_limit"],
            "daily_limit": self.thresholds["daily_limit"],
            "hourly_tx_count": hourly_tx_count,
            "max_tx_per_hour": self.thresholds["max_tx_per_hour"],
            "security_level": self.security_level.value
        }
        
        # Check 1: Single transaction limit
        if amount > self.thresholds["max_single_tx"]:
            return {
                "allowed": False,
                "reason": f"Transaction amount ({amount} {currency}) exceeds single transaction limit ({self.thresholds['max_single_tx']} {currency})",
                "requires_approval": True,
                "approval_id": await self._create_approval_request(from_address, to_address, amount, currency, "exceeds_single_tx_limit"),
                "limits_info": limits_info
            }
        
        # Check 2: Hourly spending limit
        if hourly_spent + amount > self.thresholds["hourly_limit"]:
            return {
                "allowed": False,
                "reason": f"Would exceed hourly spending limit ({hourly_spent + amount:.4f} > {self.thresholds['hourly_limit']} {currency})",
                "requires_approval": True,
                "approval_id": await self._create_approval_request(from_address, to_address, amount, currency, "exceeds_hourly_limit"),
                "limits_info": limits_info
            }
        
        # Check 3: Daily spending limit
        if daily_spent + amount > self.thresholds["daily_limit"]:
            return {
                "allowed": False,
                "reason": f"Would exceed daily spending limit ({daily_spent + amount:.4f} > {self.thresholds['daily_limit']} {currency})",
                "requires_approval": True,
                "approval_id": await self._create_approval_request(from_address, to_address, amount, currency, "exceeds_daily_limit"),
                "limits_info": limits_info
            }
        
        # Check 4: Transaction frequency
        if hourly_tx_count >= self.thresholds["max_tx_per_hour"]:
            return {
                "allowed": False,
                "reason": f"Too many transactions per hour ({hourly_tx_count} >= {self.thresholds['max_tx_per_hour']})",
                "requires_approval": True,
                "approval_id": await self._create_approval_request(from_address, to_address, amount, currency, "too_frequent"),
                "limits_info": limits_info
            }
        
        # Check 5: Approval threshold or lockdown mode
        if amount > self.thresholds["approval_threshold"] or self.thresholds["require_approval"]:
            approval_id = await self._create_approval_request(from_address, to_address, amount, currency, "requires_approval")
            return {
                "allowed": False,
                "reason": f"Transaction requires human approval (amount > {self.thresholds['approval_threshold']} {currency} or lockdown mode)",
                "requires_approval": True,
                "approval_id": approval_id,
                "limits_info": limits_info
            }
        
        # All checks passed - transaction allowed
        return {
            "allowed": True,
            "reason": "Transaction within AI spending limits",
            "requires_approval": False,
            "approval_id": None,
            "limits_info": limits_info
        }
    
    async def _get_spending(self, hours: int) -> float:
        """Get total spending in last N hours"""
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT SUM(amount) FROM ai_spending_history
                WHERE timestamp > ? AND approved = 1
            """, (cutoff,))
            result = cursor.fetchone()[0]
            return result if result else 0.0
    
    async def _get_transaction_count(self, hours: int) -> int:
        """Get transaction count in last N hours"""
        cutoff = (datetime.utcnow() - timedelta(hours=hours)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM ai_spending_history
                WHERE timestamp > ?
            """, (cutoff,))
            return cursor.fetchone()[0]
    
    async def _create_approval_request(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        currency: str,
        reason: str
    ) -> str:
        """Create an approval request"""
        import uuid
        
        approval_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        expires_at = (datetime.utcnow() + timedelta(hours=24)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO approval_requests 
                (id, timestamp, expires_at, from_address, to_address, amount, currency, reason, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (approval_id, timestamp, expires_at, from_address, to_address, amount, currency, reason, ApprovalStatus.PENDING.value))
            conn.commit()
        
        logger.info(f"Created approval request {approval_id} for {amount} {currency}")
        return approval_id
    
    async def record_transaction(
        self,
        from_address: str,
        to_address: str,
        amount: float,
        currency: str = "ETH",
        approved: bool = True,
        approval_id: Optional[str] = None,
        notes: Optional[str] = None
    ):
        """Record a transaction in AI spending history"""
        timestamp = datetime.utcnow().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ai_spending_history
                (timestamp, from_address, to_address, amount, currency, approved, approval_id, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (timestamp, from_address, to_address, amount, currency, approved, approval_id, notes))
            conn.commit()
        
        logger.info(f"Recorded AI transaction: {amount} {currency} from {from_address[:10]}... to {to_address[:10]}...")
    
    async def get_approval_requests(self, status: Optional[ApprovalStatus] = None) -> List[Dict[str, Any]]:
        """Get approval requests"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if status:
                cursor.execute("SELECT * FROM approval_requests WHERE status = ? ORDER BY timestamp DESC", (status.value,))
            else:
                cursor.execute("SELECT * FROM approval_requests ORDER BY timestamp DESC")
            
            return [dict(row) for row in cursor.fetchall()]
    
    async def approve_request(self, approval_id: str, approved_by: str = "admin") -> bool:
        """Approve a pending request"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE approval_requests
                SET status = ?, approved_at = ?, approved_by = ?
                WHERE id = ? AND status = ?
            """, (ApprovalStatus.APPROVED.value, datetime.utcnow().isoformat(), approved_by, approval_id, ApprovalStatus.PENDING.value))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Approved request {approval_id} by {approved_by}")
                return True
            return False
    
    async def reject_request(self, approval_id: str, approved_by: str = "admin") -> bool:
        """Reject a pending request"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE approval_requests
                SET status = ?, approved_at = ?, approved_by = ?
                WHERE id = ? AND status = ?
            """, (ApprovalStatus.REJECTED.value, datetime.utcnow().isoformat(), approved_by, approval_id, ApprovalStatus.PENDING.value))
            conn.commit()
            
            if cursor.rowcount > 0:
                logger.info(f"Rejected request {approval_id} by {approved_by}")
                return True
            return False
    
    async def get_spending_summary(self) -> Dict[str, Any]:
        """Get spending summary"""
        return {
            "last_hour": await self._get_spending(hours=1),
            "last_24_hours": await self._get_spending(hours=24),
            "last_7_days": await self._get_spending(hours=24*7),
            "hourly_limit": self.thresholds["hourly_limit"],
            "daily_limit": self.thresholds["daily_limit"],
            "security_level": self.security_level.value,
            "transactions_last_hour": await self._get_transaction_count(hours=1),
            "transactions_last_24_hours": await self._get_transaction_count(hours=24)
        }

