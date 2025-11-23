"""
AI Intent Parser - Phase 4
Parse natural language requests into structured API calls
"""
import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Supported intents"""
    SEND_TRANSACTION = "send_transaction"
    CHECK_BALANCE = "check_balance"
    CREATE_WALLET = "create_wallet"
    CREATE_RULE = "create_rule"
    CHECK_STATUS = "check_status"
    GET_TOKEN_BALANCE = "get_token_balance"
    UNKNOWN = "unknown"


class IntentParser:
    """
    Parse natural language into structured requests
    
    Examples:
    - "Send 0.5 ETH to 0x123..." → {intent: SEND_TRANSACTION, amount: 0.5, address: "0x123..."}
    - "What's my balance?" → {intent: CHECK_BALANCE}
    - "Create a daily spending limit of 1 ETH" → {intent: CREATE_RULE, type: "spending_limit", amount: 1}
    """
    
    def __init__(self):
        # Patterns for intent detection
        self.intent_patterns = {
            Intent.SEND_TRANSACTION: [
                r"send\s+(\d+\.?\d*)\s+(eth|matic|bnb)\s+to\s+(0x[a-fA-F0-9]+|\w+)",
                r"transfer\s+(\d+\.?\d*)\s+(eth|matic|bnb)\s+to\s+(0x[a-fA-F0-9]+|\w+)",
                r"pay\s+(0x[a-fA-F0-9]+|\w+)\s+(\d+\.?\d*)\s+(eth|matic|bnb)",
            ],
            Intent.CHECK_BALANCE: [
                r"what'?s?\s+my\s+balance",
                r"check\s+balance",
                r"how\s+much\s+(eth|matic|bnb)\s+do\s+i\s+have",
                r"show\s+balance",
            ],
            Intent.CREATE_WALLET: [
                r"create\s+(?:a\s+)?(?:new\s+)?wallet",
                r"new\s+wallet",
                r"make\s+(?:a\s+)?wallet",
            ],
            Intent.CREATE_RULE: [
                r"create\s+(?:a\s+)?(?:daily|weekly|monthly)\s+(?:spending\s+)?limit\s+of\s+(\d+\.?\d*)\s+(eth|matic|bnb)",
                r"set\s+(?:a\s+)?(?:daily|weekly|monthly)\s+limit\s+(?:to\s+)?(\d+\.?\d*)\s+(eth|matic|bnb)",
                r"limit\s+spending\s+to\s+(\d+\.?\d*)\s+(eth|matic|bnb)\s+(?:per\s+)?(day|week|month)",
            ],
            Intent.CHECK_STATUS: [
                r"check\s+(?:transaction\s+)?status\s+(?:of\s+)?(0x[a-fA-F0-9]{64})",
                r"(?:transaction\s+)?status\s+(0x[a-fA-F0-9]{64})",
                r"what'?s?\s+the\s+status\s+of\s+(0x[a-fA-F0-9]{64})",
            ],
            Intent.GET_TOKEN_BALANCE: [
                r"how\s+much\s+(\w+)\s+do\s+i\s+have",
                r"check\s+(\w+)\s+balance",
                r"what'?s?\s+my\s+(\w+)\s+balance",
            ],
        }
        
        # Common ENS/nickname mappings (can be extended)
        self.name_mappings = {
            "alice": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
            "bob": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4",
        }
        
        logger.info("Intent parser initialized")
    
    def parse(self, text: str) -> Dict[str, Any]:
        """
        Parse natural language text into structured intent
        
        Args:
            text: Natural language input
            
        Returns:
            Dict with intent, entities, confidence, and original text
        """
        text = text.lower().strip()
        
        # Try to match intent patterns
        intent, entities, confidence = self._match_intent(text)
        
        # Resolve names to addresses
        if entities.get('to_address'):
            entities['to_address'] = self._resolve_address(entities['to_address'])
        
        result = {
            "intent": intent.value,
            "entities": entities,
            "confidence": confidence,
            "original_text": text,
            "parsed": True if intent != Intent.UNKNOWN else False
        }
        
        logger.info(f"Parsed intent: {intent.value} (confidence: {confidence:.2f})")
        return result
    
    def _match_intent(self, text: str) -> Tuple[Intent, Dict[str, Any], float]:
        """
        Match text against intent patterns
        
        Returns:
            Tuple[Intent, entities dict, confidence score]
        """
        # Try each intent pattern
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    entities = self._extract_entities(intent, match, text)
                    confidence = self._calculate_confidence(text, pattern)
                    return intent, entities, confidence
        
        # No match found
        return Intent.UNKNOWN, {}, 0.0
    
    def _extract_entities(self, intent: Intent, match: re.Match, text: str) -> Dict[str, Any]:
        """Extract entities based on intent and regex match"""
        entities = {}
        
        if intent == Intent.SEND_TRANSACTION:
            groups = match.groups()
            if len(groups) >= 3:
                # Pattern: send X ETH to 0x...
                if groups[0] and groups[0][0].isdigit():
                    entities['amount'] = float(groups[0])
                    entities['currency'] = groups[1].upper()
                    entities['to_address'] = groups[2]
                # Pattern: pay 0x... X ETH
                elif groups[1] and groups[1][0].isdigit():
                    entities['to_address'] = groups[0]
                    entities['amount'] = float(groups[1])
                    entities['currency'] = groups[2].upper()
        
        elif intent == Intent.CREATE_RULE:
            groups = match.groups()
            if len(groups) >= 2:
                entities['amount'] = float(groups[0])
                entities['currency'] = groups[1].upper()
                
                # Determine period type
                if 'daily' in text or 'day' in text:
                    entities['period'] = 'daily'
                elif 'weekly' in text or 'week' in text:
                    entities['period'] = 'weekly'
                elif 'monthly' in text or 'month' in text:
                    entities['period'] = 'monthly'
                else:
                    entities['period'] = 'daily'  # default
        
        elif intent == Intent.CHECK_STATUS:
            groups = match.groups()
            if groups:
                entities['tx_hash'] = groups[0]
        
        elif intent == Intent.GET_TOKEN_BALANCE:
            groups = match.groups()
            if groups:
                entities['token'] = groups[0].upper()
        
        return entities
    
    def _resolve_address(self, address_or_name: str) -> str:
        """
        Resolve ENS name or nickname to address
        
        Args:
            address_or_name: Ethereum address or name
            
        Returns:
            Ethereum address
        """
        # If already a full address, return as-is
        if address_or_name.startswith('0x') and len(address_or_name) >= 40:
            return address_or_name
        
        # Check nickname mappings
        name_lower = address_or_name.lower()
        if name_lower in self.name_mappings:
            return self.name_mappings[name_lower]
        
        # If it starts with 0x but is short (like 0x123...), pad it for testing
        if address_or_name.startswith('0x'):
            # Pad short addresses to 42 chars for testing
            return address_or_name + '0' * (42 - len(address_or_name))
        
        # Could add ENS resolution here in the future
        # For now, return as-is and let validation catch it
        return address_or_name
    
    def _calculate_confidence(self, text: str, pattern: str) -> float:
        """
        Calculate confidence score for the match
        
        Returns:
            Float between 0 and 1
        """
        # Simple confidence based on match quality
        confidence = 0.8  # Base confidence for pattern match
        
        # Increase confidence if text is short and matches well
        if len(text.split()) <= 10:
            confidence += 0.1
        
        # Decrease confidence if text is very long or complex
        if len(text.split()) > 20:
            confidence -= 0.2
        
        return min(max(confidence, 0.0), 1.0)
    
    def to_api_request(self, parsed: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Convert parsed intent to API request format
        
        Args:
            parsed: Output from parse()
            
        Returns:
            Dict with endpoint and parameters, or None if can't convert
        """
        if not parsed.get('parsed'):
            return None
        
        intent = parsed['intent']
        entities = parsed['entities']
        
        # Map intent to API endpoint and parameters
        if intent == Intent.SEND_TRANSACTION.value:
            return {
                'endpoint': 'POST /api/v1/transaction/send',
                'params': {
                    'to_address': entities.get('to_address'),
                    'value': entities.get('amount'),
                }
            }
        
        elif intent == Intent.CHECK_BALANCE.value:
            return {
                'endpoint': 'GET /api/v1/wallet/balance',
                'params': {}
            }
        
        elif intent == Intent.CREATE_WALLET.value:
            return {
                'endpoint': 'POST /api/v1/wallet/create',
                'params': {
                    'wallet_name': f"wallet_{int(time.time())}"
                }
            }
        
        elif intent == Intent.CREATE_RULE.value:
            return {
                'endpoint': 'POST /api/v1/rules/create',
                'params': {
                    'rule_type': 'spending_limit',
                    'rule_name': f"{entities.get('period', 'daily').capitalize()} Limit",
                    'parameters': {
                        'type': entities.get('period', 'daily'),
                        'amount': entities.get('amount')
                    },
                    'action': 'deny'
                }
            }
        
        elif intent == Intent.CHECK_STATUS.value:
            return {
                'endpoint': f"GET /api/v1/transaction/{entities.get('tx_hash')}",
                'params': {}
            }
        
        elif intent == Intent.GET_TOKEN_BALANCE.value:
            return {
                'endpoint': f"GET /api/v1/token/balance/{entities.get('token', 'USDC')}",
                'params': {}
            }
        
        return None
    
    def add_name_mapping(self, name: str, address: str):
        """Add a new name-to-address mapping"""
        self.name_mappings[name.lower()] = address
        logger.info(f"Added mapping: {name} → {address}")


import time

