"""
Rule & Risk Engine - Phase 3
Automated safety controls and risk management
"""
import logging
import sqlite3
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json

logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Types of rules that can be applied"""
    SPENDING_LIMIT = "spending_limit"
    ADDRESS_WHITELIST = "address_whitelist"
    ADDRESS_BLACKLIST = "address_blacklist"
    TIME_RESTRICTION = "time_restriction"
    AMOUNT_THRESHOLD = "amount_threshold"
    DAILY_TRANSACTION_COUNT = "daily_transaction_count"
    

class RuleAction(Enum):
    """Actions that rules can take"""
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class RiskLevel(Enum):
    """Risk levels for transactions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Rule:
    """Represents a single rule"""
    
    def __init__(
        self,
        rule_id: int,
        rule_type: str,
        rule_name: str,
        parameters: Dict[str, Any],
        action: str,
        enabled: bool = True,
        priority: int = 0
    ):
        self.rule_id = rule_id
        self.rule_type = RuleType(rule_type)
        self.rule_name = rule_name
        self.parameters = parameters
        self.action = RuleAction(action)
        self.enabled = enabled
        self.priority = priority
    
    def check(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if transaction passes this rule
        
        Returns:
            Tuple[bool, str]: (passes, reason)
        """
        if not self.enabled:
            return True, "Rule disabled"
        
        if self.rule_type == RuleType.SPENDING_LIMIT:
            return self._check_spending_limit(transaction, context)
        elif self.rule_type == RuleType.ADDRESS_WHITELIST:
            return self._check_whitelist(transaction)
        elif self.rule_type == RuleType.ADDRESS_BLACKLIST:
            return self._check_blacklist(transaction)
        elif self.rule_type == RuleType.TIME_RESTRICTION:
            return self._check_time_restriction()
        elif self.rule_type == RuleType.AMOUNT_THRESHOLD:
            return self._check_amount_threshold(transaction)
        elif self.rule_type == RuleType.DAILY_TRANSACTION_COUNT:
            return self._check_daily_count(context)
        
        return True, "Unknown rule type"
    
    def _check_spending_limit(self, transaction: Dict[str, Any], context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check spending limit rule"""
        limit_type = self.parameters.get('type', 'daily')  # daily, weekly, monthly, per_transaction
        limit_amount = float(self.parameters.get('amount', 0))
        tx_amount = float(transaction.get('value', 0))
        
        if limit_type == 'per_transaction':
            if tx_amount > limit_amount:
                return False, f"Transaction amount ({tx_amount}) exceeds per-transaction limit ({limit_amount})"
            return True, "Within per-transaction limit"
        
        # For period limits, check context for recent spending
        period_spending = context.get(f'{limit_type}_spending', 0)
        total_after_tx = period_spending + tx_amount
        
        if total_after_tx > limit_amount:
            return False, f"Would exceed {limit_type} limit ({limit_amount}). Current: {period_spending}, Transaction: {tx_amount}"
        
        return True, f"Within {limit_type} limit"
    
    def _check_whitelist(self, transaction: Dict[str, Any]) -> Tuple[bool, str]:
        """Check address whitelist"""
        allowed_addresses = [addr.lower() for addr in self.parameters.get('addresses', [])]
        to_address = transaction.get('to_address', '').lower()
        
        if to_address in allowed_addresses:
            return True, "Address is whitelisted"
        
        return False, f"Address {to_address} not in whitelist"
    
    def _check_blacklist(self, transaction: Dict[str, Any]) -> Tuple[bool, str]:
        """Check address blacklist"""
        blocked_addresses = [addr.lower() for addr in self.parameters.get('addresses', [])]
        to_address = transaction.get('to_address', '').lower()
        
        if to_address in blocked_addresses:
            return False, f"Address {to_address} is blacklisted"
        
        return True, "Address not blacklisted"
    
    def _check_time_restriction(self) -> Tuple[bool, str]:
        """Check time-based restrictions"""
        allowed_hours = self.parameters.get('allowed_hours', '00:00-23:59')
        timezone = self.parameters.get('timezone', 'UTC')
        
        # Simple implementation - parse hours
        start_time, end_time = allowed_hours.split('-')
        start_hour = int(start_time.split(':')[0])
        end_hour = int(end_time.split(':')[0])
        
        current_hour = datetime.utcnow().hour  # Simplified - should use proper timezone
        
        if start_hour <= current_hour <= end_hour:
            return True, "Within allowed time window"
        
        return False, f"Outside allowed time window ({allowed_hours} {timezone})"
    
    def _check_amount_threshold(self, transaction: Dict[str, Any]) -> Tuple[bool, str]:
        """Check amount threshold for approval requirement"""
        threshold = float(self.parameters.get('threshold', 0))
        tx_amount = float(transaction.get('value', 0))
        
        if tx_amount >= threshold:
            return False, f"Amount ({tx_amount}) exceeds threshold ({threshold}) - requires approval"
        
        return True, "Below threshold"
    
    def _check_daily_count(self, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Check daily transaction count"""
        max_count = int(self.parameters.get('max_count', 10))
        current_count = context.get('daily_transaction_count', 0)
        
        if current_count >= max_count:
            return False, f"Daily transaction limit reached ({max_count})"
        
        return True, f"Within daily transaction limit ({current_count}/{max_count})"


class RuleEngine:
    """
    Main Rule Engine - evaluates transactions against rules
    """
    
    def __init__(self, db_path: str = "chainpilot.db"):
        self.db_path = db_path
        self._initialize_database()
        logger.info(f"Rule Engine initialized with database: {db_path}")
    
    def _initialize_database(self):
        """Initialize rules database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rule_type TEXT NOT NULL,
                    rule_name TEXT NOT NULL,
                    parameters TEXT NOT NULL,
                    action TEXT NOT NULL,
                    enabled INTEGER DEFAULT 1,
                    priority INTEGER DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create rule evaluations table (audit trail)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS rule_evaluations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tx_hash TEXT,
                    rule_id INTEGER,
                    rule_name TEXT,
                    passed INTEGER,
                    reason TEXT,
                    timestamp TEXT NOT NULL,
                    FOREIGN KEY(rule_id) REFERENCES rules(id)
                )
            """)
            
            conn.commit()
            logger.info("Rule engine database initialized")
    
    def create_rule(
        self,
        rule_type: str,
        rule_name: str,
        parameters: Dict[str, Any],
        action: str,
        enabled: bool = True,
        priority: int = 0
    ) -> int:
        """Create a new rule"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            now = datetime.utcnow().isoformat()
            cursor.execute(
                """
                INSERT INTO rules (rule_type, rule_name, parameters, action, enabled, priority, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (rule_type, rule_name, json.dumps(parameters), action, 1 if enabled else 0, priority, now, now)
            )
            
            rule_id = cursor.lastrowid
            conn.commit()
            
            logger.info(f"Created rule: {rule_name} (ID: {rule_id}, Type: {rule_type})")
            return rule_id
    
    def get_rules(self, enabled_only: bool = True) -> List[Rule]:
        """Get all rules"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT id, rule_type, rule_name, parameters, action, enabled, priority FROM rules"
            if enabled_only:
                query += " WHERE enabled = 1"
            query += " ORDER BY priority DESC"
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            rules = []
            for row in rows:
                rule = Rule(
                    rule_id=row[0],
                    rule_type=row[1],
                    rule_name=row[2],
                    parameters=json.loads(row[3]),
                    action=row[4],
                    enabled=bool(row[5]),
                    priority=row[6]
                )
                rules.append(rule)
            
            return rules
    
    def evaluate_transaction(
        self,
        transaction: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a transaction against all rules
        
        Args:
            transaction: Transaction details (to_address, value, etc.)
            context: Additional context (recent spending, tx count, etc.)
        
        Returns:
            Dict with evaluation result:
            - allowed: bool
            - action: allow, deny, require_approval
            - risk_level: low, medium, high, critical
            - failed_rules: List of failed rule names
            - reasons: List of failure reasons
        """
        if context is None:
            context = self._build_context(transaction)
        
        rules = self.get_rules(enabled_only=True)
        
        failed_rules = []
        reasons = []
        action = RuleAction.ALLOW
        
        # Evaluate each rule
        for rule in rules:
            passed, reason = rule.check(transaction, context)
            
            # Log evaluation
            self._log_evaluation(
                tx_hash=transaction.get('tx_hash', 'pending'),
                rule_id=rule.rule_id,
                rule_name=rule.rule_name,
                passed=passed,
                reason=reason
            )
            
            if not passed:
                failed_rules.append(rule.rule_name)
                reasons.append(reason)
                
                # Determine action (most restrictive wins)
                if rule.action == RuleAction.DENY:
                    action = RuleAction.DENY
                elif rule.action == RuleAction.REQUIRE_APPROVAL and action != RuleAction.DENY:
                    action = RuleAction.REQUIRE_APPROVAL
        
        # Calculate risk level
        risk_level = self._calculate_risk(transaction, context, failed_rules)
        
        # Determine if allowed
        allowed = action == RuleAction.ALLOW
        
        result = {
            "allowed": allowed,
            "action": action.value,
            "risk_level": risk_level.value,
            "failed_rules": failed_rules,
            "reasons": reasons,
            "rules_checked": len(rules),
            "rules_passed": len(rules) - len(failed_rules)
        }
        
        logger.info(f"Transaction evaluation: {result['action']} (Risk: {result['risk_level']})")
        
        return result
    
    def _build_context(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Build context for rule evaluation"""
        from_address = transaction.get('from_address', '')
        
        # Get recent spending
        daily_spending = self._get_period_spending(from_address, days=1)
        weekly_spending = self._get_period_spending(from_address, days=7)
        monthly_spending = self._get_period_spending(from_address, days=30)
        
        # Get transaction count
        daily_tx_count = self._get_transaction_count(from_address, days=1)
        
        return {
            "daily_spending": daily_spending,
            "weekly_spending": weekly_spending,
            "monthly_spending": monthly_spending,
            "daily_transaction_count": daily_tx_count
        }
    
    def _get_period_spending(self, from_address: str, days: int) -> float:
        """Get total spending for an address over a period"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            cursor.execute(
                """
                SELECT COALESCE(SUM(CAST(value AS REAL)), 0)
                FROM transactions
                WHERE from_address = ? AND timestamp >= ? AND status IN ('confirmed', 'pending')
                """,
                (from_address, cutoff)
            )
            
            result = cursor.fetchone()
            return result[0] if result else 0.0
    
    def _get_transaction_count(self, from_address: str, days: int) -> int:
        """Get transaction count for an address over a period"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM transactions
                WHERE from_address = ? AND timestamp >= ?
                """,
                (from_address, cutoff)
            )
            
            result = cursor.fetchone()
            return result[0] if result else 0
    
    def _calculate_risk(
        self,
        transaction: Dict[str, Any],
        context: Dict[str, Any],
        failed_rules: List[str]
    ) -> RiskLevel:
        """Calculate risk level for transaction"""
        risk_score = 0
        
        # Failed rules increase risk
        risk_score += len(failed_rules) * 25
        
        # Large transaction amount
        value = float(transaction.get('value', 0))
        if value > 10:
            risk_score += 30
        elif value > 1:
            risk_score += 15
        elif value > 0.1:
            risk_score += 5
        
        # High transaction frequency
        daily_count = context.get('daily_transaction_count', 0)
        if daily_count > 50:
            risk_score += 20
        elif daily_count > 20:
            risk_score += 10
        
        # Determine level
        if risk_score >= 75:
            return RiskLevel.CRITICAL
        elif risk_score >= 50:
            return RiskLevel.HIGH
        elif risk_score >= 25:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW
    
    def _log_evaluation(
        self,
        tx_hash: str,
        rule_id: int,
        rule_name: str,
        passed: bool,
        reason: str
    ):
        """Log rule evaluation result"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO rule_evaluations (tx_hash, rule_id, rule_name, passed, reason, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (tx_hash, rule_id, rule_name, 1 if passed else 0, reason, datetime.utcnow().isoformat())
            )
            
            conn.commit()
    
    def delete_rule(self, rule_id: int) -> bool:
        """Delete a rule"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
            deleted = cursor.rowcount > 0
            conn.commit()
            
            if deleted:
                logger.info(f"Deleted rule ID: {rule_id}")
            
            return deleted
    
    def update_rule(
        self,
        rule_id: int,
        enabled: Optional[bool] = None,
        parameters: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None
    ) -> bool:
        """Update a rule"""
        updates = []
        values = []
        
        if enabled is not None:
            updates.append("enabled = ?")
            values.append(1 if enabled else 0)
        
        if parameters is not None:
            updates.append("parameters = ?")
            values.append(json.dumps(parameters))
        
        if priority is not None:
            updates.append("priority = ?")
            values.append(priority)
        
        if not updates:
            return False
        
        updates.append("updated_at = ?")
        values.append(datetime.utcnow().isoformat())
        values.append(rule_id)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            query = f"UPDATE rules SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            updated = cursor.rowcount > 0
            conn.commit()
            
            if updated:
                logger.info(f"Updated rule ID: {rule_id}")
            
            return updated

