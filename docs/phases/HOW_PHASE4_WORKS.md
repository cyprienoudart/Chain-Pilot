# 🤖 How Phase 4 AI Integration Works

## Technical Deep Dive

This document explains the technical implementation of ChainPilot's natural language processing capabilities.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     AI Agent / User                         │
│                  "Send 0.5 ETH to alice"                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  POST /api/v1/ai/parse                      │
│                  (Natural Language API)                     │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                     Intent Parser                           │
│  1. Match text against patterns                             │
│  2. Extract entities (amount, address, etc.)                │
│  3. Resolve names ("alice" → 0x742d...)                    │
│  4. Calculate confidence score                              │
│  5. Convert to API request format                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Structured Request                         │
│  {                                                          │
│    intent: "send_transaction",                             │
│    entities: {amount: 0.5, to_address: "0x742d..."},      │
│    api_request: {endpoint: "POST /transaction/send"}       │
│  }                                                          │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Execute Action                             │
│  ├─ Rule Engine (Phase 3) - Check rules                    │
│  ├─ Transaction Builder - Create transaction                │
│  ├─ Wallet Manager - Sign transaction                       │
│  └─ Audit Logger - Log action                               │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Response to AI Agent                       │
│  "✅ Sent 0.5 ETH to alice (0x742d...)"                    │
│  "TX: 0xabc123..."                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Core Components

### 1. Intent Parser (`src/ai/intent_parser.py`)

The brain of the NLP system. Converts natural language to structured data.

#### Pattern Matching
```python
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
    ],
    # ... more patterns
}
```

**How It Works:**
1. Text is converted to lowercase
2. Each pattern is tested against the text
3. First match wins (order matters!)
4. Regex groups capture entities
5. Entities are validated and formatted

#### Entity Extraction
```python
def _extract_entities(self, intent: Intent, match: re.Match, text: str):
    entities = {}
    
    if intent == Intent.SEND_TRANSACTION:
        groups = match.groups()
        if len(groups) >= 3:
            entities['amount'] = float(groups[0])
            entities['currency'] = groups[1].upper()
            entities['to_address'] = groups[2]
    
    return entities
```

**Extracted Entities:**
- `amount`: Numeric value (0.5, 1, 10.25)
- `currency`: Token symbol (ETH, MATIC, BNB)
- `to_address`: Ethereum address or name
- `period`: Time period (daily, weekly, monthly)
- `tx_hash`: Transaction hash
- `token`: Token symbol for balance queries

#### Name Resolution
```python
self.name_mappings = {
    "alice": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
    "bob": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4",
}

def _resolve_address(self, address_or_name: str) -> str:
    # If already an address, return it
    if address_or_name.startswith('0x') and len(address_or_name) >= 40:
        return address_or_name
    
    # Check mappings
    if address_or_name.lower() in self.name_mappings:
        return self.name_mappings[address_or_name.lower()]
    
    # Future: ENS resolution here
    return address_or_name
```

#### Confidence Scoring
```python
def _calculate_confidence(self, text: str, pattern: str) -> float:
    confidence = 0.8  # Base for pattern match
    
    # Short, clear text increases confidence
    if len(text.split()) <= 10:
        confidence += 0.1
    
    # Long, complex text decreases confidence
    if len(text.split()) > 20:
        confidence -= 0.2
    
    return min(max(confidence, 0.0), 1.0)
```

**Confidence Levels:**
- 0.9+ : High confidence, execute directly
- 0.7-0.9: Medium confidence, confirm first
- < 0.7: Low confidence, ask for clarification

#### API Request Conversion
```python
def to_api_request(self, parsed: Dict[str, Any]):
    intent = parsed['intent']
    entities = parsed['entities']
    
    if intent == Intent.SEND_TRANSACTION.value:
        return {
            'endpoint': 'POST /api/v1/transaction/send',
            'params': {
                'to_address': entities.get('to_address'),
                'value': entities.get('amount'),
            }
        }
    # ... more mappings
```

---

### 2. Natural Language API (`src/api/ai_routes.py`)

RESTful endpoints for AI integration.

#### Parse Endpoint
```python
@router.post("/ai/parse")
async def parse_natural_language(
    request: Request,
    nl_request: NaturalLanguageRequest
):
    # 1. Parse the text
    parsed = intent_parser.parse(nl_request.text)
    
    # 2. Convert to API request
    api_request = intent_parser.to_api_request(parsed)
    
    # 3. Check if confirmation needed
    needs_confirmation = _needs_confirmation(parsed, nl_request.confirm)
    
    # 4. Optionally execute
    if nl_request.execute and parsed['confidence'] > 0.7:
        if needs_confirmation:
            return {"status": "pending_confirmation"}
        else:
            result = await _execute_action(request, api_request, parsed)
            return {"status": "executed", "execution": result}
    
    return {
        "intent": parsed['intent'],
        "entities": parsed['entities'],
        "confidence": parsed['confidence'],
        "api_request": api_request,
        "needs_confirmation": needs_confirmation
    }
```

#### Execute Endpoint
```python
@router.post("/ai/execute")
async def execute_parsed_intent(
    request: Request,
    intent: str,
    entities: Dict[str, Any]
):
    # Reconstruct parsed format
    parsed = {"intent": intent, "entities": entities, "parsed": True}
    
    # Convert to API request
    api_request = intent_parser.to_api_request(parsed)
    
    # Execute
    result = await _execute_action(request, api_request, parsed)
    
    return {"message": "Action executed successfully", "result": result}
```

#### Action Execution
```python
async def _execute_action(request: Request, api_request: Dict, parsed: Dict):
    intent = parsed['intent']
    
    if intent == Intent.SEND_TRANSACTION.value:
        # Use existing transaction endpoint
        tx_request = TransactionSendRequest(
            to_address=params['to_address'],
            value=params['value']
        )
        result = await send_transaction_route(request, tx_request)
        return {"type": "transaction", "data": result}
    
    elif intent == Intent.CHECK_BALANCE.value:
        # Get balance directly
        wallet_manager = request.app.state.wallet_manager
        web3_manager = request.app.state.web3_manager
        
        balance = web3_manager.get_balance(wallet_manager.current_wallet.address)
        return {"type": "balance", "data": {"balance_ether": balance}}
    
    # ... more intent handlers
```

---

## Data Flow Examples

### Example 1: Send Transaction

```
INPUT: "Send 0.5 ETH to alice"
```

**Step 1: Pattern Matching**
```python
Pattern: r"send\s+(\d+\.?\d*)\s+(eth|matic|bnb)\s+to\s+(0x[a-fA-F0-9]+|\w+)"
Match: ✅ groups = ('0.5', 'eth', 'alice')
```

**Step 2: Entity Extraction**
```python
entities = {
    'amount': 0.5,
    'currency': 'ETH',
    'to_address': 'alice'  # Not resolved yet
}
```

**Step 3: Name Resolution**
```python
'alice' → '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7'

entities['to_address'] = '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7'
```

**Step 4: Confidence Calculation**
```python
Base: 0.8
Short text (+0.1): 0.9
Final confidence: 0.9
```

**Step 5: API Request Format**
```json
{
  "endpoint": "POST /api/v1/transaction/send",
  "params": {
    "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
    "value": 0.5
  }
}
```

**Step 6: Execution (if execute=true)**
```python
1. Check if confirmation needed (amount > 0.1 ETH → yes)
2. If confirmed:
   - Build transaction
   - Evaluate rules (Phase 3)
   - Sign transaction
   - Broadcast to blockchain
   - Log in audit database
3. Return result to AI agent
```

---

### Example 2: Check Balance

```
INPUT: "What's my balance?"
```

**Step 1: Pattern Matching**
```python
Pattern: r"what'?s?\s+my\s+balance"
Match: ✅
```

**Step 2: Entity Extraction**
```python
entities = {}  # No entities needed for balance check
```

**Step 3: Confidence Calculation**
```python
Base: 0.8
Short text (+0.1): 0.9
Final confidence: 0.9
```

**Step 4: API Request Format**
```json
{
  "endpoint": "GET /api/v1/wallet/balance",
  "params": {}
}
```

**Step 5: Execution**
```python
1. Get wallet_manager.current_wallet.address
2. Query web3_manager.get_balance(address)
3. Convert wei to ether
4. Return result
```

**Step 6: Response**
```json
{
  "status": "executed",
  "execution": {
    "type": "balance",
    "data": {
      "balance_wei": "100000000000000000000",
      "balance_ether": 100.0,
      "currency": "ETH"
    }
  }
}
```

---

### Example 3: Create Rule

```
INPUT: "Create a daily spending limit of 1 ETH"
```

**Step 1: Pattern Matching**
```python
Pattern: r"create\s+(?:a\s+)?(?:daily|weekly|monthly)\s+(?:spending\s+)?limit\s+of\s+(\d+\.?\d*)\s+(eth|matic|bnb)"
Match: ✅ groups = ('1', 'eth')
```

**Step 2: Entity Extraction**
```python
entities = {
    'amount': 1.0,
    'currency': 'ETH',
    'period': 'daily'  # Extracted from 'daily' in text
}
```

**Step 3: API Request Format**
```json
{
  "endpoint": "POST /api/v1/rules/create",
  "params": {
    "rule_type": "spending_limit",
    "rule_name": "Daily Limit",
    "parameters": {
      "type": "daily",
      "amount": 1.0
    },
    "action": "deny"
  }
}
```

**Step 4: Execution**
```python
1. Call rule_engine.create_rule(...)
2. Store rule in database
3. Return rule ID and details
```

---

## Integration Patterns

### Pattern 1: Parse-Confirm-Execute
```python
# Step 1: Parse without executing
response = requests.post("/api/v1/ai/parse", json={
    "text": "Send 0.5 ETH to alice",
    "execute": False
})

# Step 2: Show to user, get confirmation
if response.json()["needs_confirmation"]:
    user_confirms = ask_user("Confirm: Send 0.5 ETH to alice?")
    
    # Step 3: Execute if confirmed
    if user_confirms:
        execute_response = requests.post("/api/v1/ai/execute", json={
            "intent": "send_transaction",
            "entities": response.json()["entities"]
        })
```

### Pattern 2: Auto-Execute Safe Actions
```python
# Check balance doesn't need confirmation
response = requests.post("/api/v1/ai/parse", json={
    "text": "What's my balance?",
    "execute": True,
    "confirm": False  # Don't require confirmation
})

# Executed immediately
balance = response.json()["execution"]["data"]["balance_ether"]
```

### Pattern 3: Confidence-Based Decision
```python
response = requests.post("/api/v1/ai/parse", json={
    "text": user_input,
    "execute": False
})

confidence = response.json()["confidence"]

if confidence > 0.9:
    # High confidence - execute directly
    execute_action(response.json())
elif confidence > 0.7:
    # Medium - confirm first
    if confirm_with_user(response.json()):
        execute_action(response.json())
else:
    # Low - ask for clarification
    ask_user_to_clarify()
```

---

## Security Considerations

### 1. Rule Engine Integration
All natural language transactions go through the Rule Engine:

```python
# In execute_action()
if intent == Intent.SEND_TRANSACTION.value:
    # Build transaction
    tx = build_transaction(...)
    
    # Evaluate rules (Phase 3)
    rule_result = rule_engine.evaluate_transaction(tx)
    
    if rule_result["action"] == "deny":
        return {"error": "Transaction denied by rules", "reason": rule_result["reason"]}
    
    # Continue with transaction if allowed
    signed_tx = sign_transaction(tx)
    broadcast(signed_tx)
```

### 2. Confirmation Requirements
```python
def _needs_confirmation(parsed: Dict, confirm_enabled: bool) -> bool:
    if not confirm_enabled:
        return False
    
    intent = parsed['intent']
    
    # Always confirm transactions
    if intent == Intent.SEND_TRANSACTION.value:
        amount = parsed['entities'].get('amount', 0)
        if amount > 0.1:  # Large amounts
            return True
        return True  # All transactions need confirmation
    
    # Confirm rule creation
    if intent == Intent.CREATE_RULE.value:
        return True
    
    # Read-only operations don't need confirmation
    return False
```

### 3. Input Validation
```python
# In intent parser
def parse(self, text: str) -> Dict:
    # Validate text length
    if len(text) > 500:
        raise ValueError("Text too long")
    
    # Sanitize input
    text = text.strip().lower()
    
    # Parse
    intent, entities, confidence = self._match_intent(text)
    
    # Validate entities
    if entities.get('to_address'):
        if not is_valid_address(entities['to_address']):
            confidence *= 0.5  # Reduce confidence for invalid address
    
    return {"intent": intent, "entities": entities, "confidence": confidence}
```

---

## Performance Considerations

### 1. Pattern Matching Performance
- Regex matching is fast (microseconds)
- Patterns are tested in order (most common first)
- No external API calls needed

### 2. Caching
```python
# Could add caching for repeated queries
from functools import lru_cache

@lru_cache(maxsize=128)
def parse_cached(text: str):
    return intent_parser.parse(text)
```

### 3. Async Execution
All API endpoints are async:
```python
async def parse_natural_language(...):
    # Parse is sync (fast)
    parsed = intent_parser.parse(text)
    
    # Execution is async (may involve blockchain calls)
    if execute:
        result = await _execute_action(request, api_request, parsed)
```

---

## Testing Strategy

### Unit Tests (Intent Parser)
```python
def test_send_transaction_parsing():
    parser = IntentParser()
    
    result = parser.parse("Send 0.5 ETH to 0x742d...")
    
    assert result['intent'] == 'send_transaction'
    assert result['entities']['amount'] == 0.5
    assert result['entities']['currency'] == 'ETH'
    assert result['confidence'] > 0.8
```

### Integration Tests (API)
```python
def test_parse_and_execute():
    response = client.post("/api/v1/ai/parse", json={
        "text": "What's my balance?",
        "execute": True
    })
    
    assert response.status_code == 200
    assert response.json()["status"] == "executed"
    assert "balance_ether" in response.json()["execution"]["data"]
```

### End-to-End Tests
```bash
# test_phase4.py
python3 test_phase4.py

# Tests:
# ✅ Get examples
# ✅ Parse send transaction
# ✅ Parse check balance
# ✅ Parse create rule
# ✅ Add name mapping
# ✅ Parse with name
# ✅ Execute balance check
# ✅ Multiple intents
# ✅ Confidence scores
```

---

## Future Enhancements

### 1. Advanced NLP
```python
# Current: Regex patterns
r"send\s+(\d+\.?\d*)\s+(eth)"

# Future: Transformer models
from transformers import pipeline
nlp = pipeline("text-classification", model="chainpilot/intent-classifier")
result = nlp("Send 0.5 ETH to alice")
```

### 2. Context Awareness
```python
class ConversationContext:
    def __init__(self):
        self.history = []
        self.last_intent = None
        self.last_entities = {}
    
    def parse_with_context(self, text: str):
        # "Send to alice" + context from "0.5 ETH" earlier
        if "send" in text and not has_amount(text):
            # Use amount from previous message
            text = f"Send {self.last_entities['amount']} ETH to {extract_address(text)}"
        
        return intent_parser.parse(text)
```

### 3. ENS Resolution
```python
from ens import ENS

def _resolve_address(self, address_or_name: str) -> str:
    # Check nicknames first
    if address_or_name in self.name_mappings:
        return self.name_mappings[address_or_name]
    
    # Check ENS
    if address_or_name.endswith('.eth'):
        ens = ENS.fromWeb3(web3)
        resolved = ens.address(address_or_name)
        if resolved:
            return resolved
    
    return address_or_name
```

---

## Summary

Phase 4 AI Integration provides:
- ✅ Natural language understanding
- ✅ Entity extraction
- ✅ Name resolution
- ✅ Confidence scoring
- ✅ Action execution
- ✅ Security integration (Rules Phase 3)
- ✅ Comprehensive testing

**Result:** AI agents can now interact with ChainPilot using plain English instead of complex API calls!

---

## Related Documentation
- [PHASE4_COMPLETE.md](PHASE4_COMPLETE.md) - Phase 4 overview
- [README.md](README.md) - Project overview
- [HOW_IT_WORKS.md](HOW_IT_WORKS.md) - Overall architecture

