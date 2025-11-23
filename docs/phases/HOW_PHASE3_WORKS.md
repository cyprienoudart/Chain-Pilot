# How Phase 3 Works - Rule Engine & Automation

## 🎯 Overview

Phase 3 adds **automated safety controls** that evaluate EVERY transaction before it executes. Think of it as a smart bouncer for your crypto transactions - automatically allowing safe ones, blocking dangerous ones, and flagging suspicious ones for review.

---

## 🏗️ Architecture

```
Transaction Request
        ↓
  ┌─────────────┐
  │ API Endpoint│
  └──────┬──────┘
         │
         ▼
  ┌─────────────┐
  │Rule Engine  │ ← Evaluates ALL rules
  │             │   (spending limits, whitelists, etc.)
  └──────┬──────┘
         │
         ├─ ALL PASS → ✅ Execute Transaction
         ├─ DENY RULE FAILS → ❌ Block Transaction
         └─ APPROVAL RULE → ⚠️ Flag for Review
         │
         ▼
  ┌─────────────┐
  │Audit Logger │ ← Records decision
  └─────────────┘
```

---

## 🔧 Components

### 1. Rule Engine (`src/rules/rule_engine.py`)

**What it does:**
- Stores rules in SQLite database
- Evaluates transactions against all enabled rules
- Calculates risk scores
- Determines final action (ALLOW/DENY/REQUIRE_APPROVAL)

**Key Classes:**
- `Rule`: Represents a single rule with type, parameters, and action
- `RuleEngine`: Main engine that evaluates transactions

### 2. Rule Types

Six types of rules available:

1. **Spending Limit** - Control per-tx, daily, weekly, monthly spending
2. **Address Whitelist** - Only allow specific addresses
3. **Address Blacklist** - Block specific addresses
4. **Time Restriction** - Only allow during certain hours
5. **Amount Threshold** - Require approval for large amounts
6. **Daily TX Count** - Limit number of transactions per day

### 3. Rule Actions

Rules can take three actions:

- **ALLOW**: Explicitly approve (overrides other rules)
- **DENY**: Block transaction immediately
- **REQUIRE_APPROVAL**: Flag for manual review

### 4. Risk Scoring

Every transaction gets a risk score:

- **LOW**: Normal transaction, within all limits
- **MEDIUM**: Some unusual activity
- **HIGH**: Multiple rule violations or large amount
- **CRITICAL**: Serious violations, likely malicious

---

## 💡 How It Works - Step by Step

### Example 1: Transaction Within Limits

```python
# Rule: Max 0.5 ETH per transaction
# Request: Send 0.1 ETH

1. User requests: POST /transaction/send {"value": 0.1}
2. Rule Engine checks: 0.1 < 0.5 ✅
3. Action: ALLOW
4. Transaction executes automatically
5. Logged: "Transaction allowed, risk: LOW"
```

### Example 2: Transaction Over Limit

```python
# Rule: Max 0.5 ETH per transaction
# Request: Send 2.0 ETH

1. User requests: POST /transaction/send {"value": 2.0}
2. Rule Engine checks: 2.0 > 0.5 ❌
3. Action: DENY
4. Response: {
     "status": "blocked",
     "reason": "Exceeds per-transaction limit",
     "risk_level": "high"
   }
5. Transaction NEVER reaches blockchain
6. Logged: "Transaction blocked by: spending_limit"
```

### Example 3: Approval Required

```python
# Rule 1: Max 0.5 ETH per transaction (DENY)
# Rule 2: Amounts > 0.3 ETH need approval (REQUIRE_APPROVAL)
# Request: Send 0.4 ETH

1. User requests: POST /transaction/send {"value": 0.4}
2. Rule Engine checks:
   - Rule 1: 0.4 < 0.5 ✅ (passes)
   - Rule 2: 0.4 > 0.3 ❌ (triggers approval)
3. Action: REQUIRE_APPROVAL
4. Response: {
     "status": "requires_approval",
     "risk_level": "medium"
   }
5. Transaction flagged for manual review
6. Logged: "Transaction pending approval"
```

---

## 🎮 Using the API

### Create a Rule

```bash
curl -X POST http://localhost:8000/api/v1/rules/create \
  -H "Content-Type: application/json" \
  -d '{
    "rule_type": "spending_limit",
    "rule_name": "Daily Budget",
    "parameters": {"type": "daily", "amount": 1.0},
    "action": "deny"
  }'
```

### Test a Transaction

```bash
# Check IF transaction would be allowed (doesn't execute)
curl -X POST "http://localhost:8000/api/v1/rules/evaluate?to_address=0x123...&value=0.5"
```

### Send Transaction (With Rules)

```bash
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
    "value": 0.1
  }'

# Rules are AUTOMATICALLY checked
# Transaction executes only if rules pass
```

### Get All Rules

```bash
curl http://localhost:8000/api/v1/rules
```

### Get Rule Templates

```bash
curl http://localhost:8000/api/v1/rules/templates
```

---

## 🔒 Security Features

### 1. Automatic Enforcement

- Rules CANNOT be bypassed (except with `skip_rules=true` admin flag)
- Every transaction checked before execution
- No way to "forget" to check rules

### 2. Audit Trail

- Every rule evaluation logged
- Includes: timestamp, rule name, result, reason
- Complete history for compliance

### 3. Priority System

- Rules have priority (higher = evaluated first)
- Most restrictive action wins (DENY > REQUIRE_APPROVAL > ALLOW)
- Predictable, deterministic behavior

### 4. Context-Aware

- Rules consider historical spending
- Tracks transaction counts
- Calculates risk based on patterns

---

## 🧪 Testing

```bash
# 1. Start server in sandbox mode
python3 run.py --sandbox

# 2. Run Phase 3 tests
python3 test_phase3.py

# Expected results:
# ✅ Create rules
# ✅ Block over-limit transactions
# ✅ Allow within-limit transactions
# ✅ Require approval for large amounts
# ✅ Rule priorities work correctly
```

---

## 📊 Database Schema

### Rules Table

```sql
CREATE TABLE rules (
    id INTEGER PRIMARY KEY,
    rule_type TEXT NOT NULL,
    rule_name TEXT NOT NULL,
    parameters TEXT NOT NULL,  -- JSON
    action TEXT NOT NULL,      -- allow, deny, require_approval
    enabled INTEGER DEFAULT 1,
    priority INTEGER DEFAULT 0,
    created_at TEXT,
    updated_at TEXT
)
```

### Rule Evaluations Table

```sql
CREATE TABLE rule_evaluations (
    id INTEGER PRIMARY KEY,
    tx_hash TEXT,
    rule_id INTEGER,
    rule_name TEXT,
    passed INTEGER,        -- 0 or 1
    reason TEXT,
    timestamp TEXT,
    FOREIGN KEY(rule_id) REFERENCES rules(id)
)
```

---

## 🎯 Real-World Use Cases

### 1. AI Agent Safety

**Scenario:** AI agent autonomously managing a trading bot

**Rules:**
- Max 0.1 ETH per transaction
- Daily limit: 1 ETH
- Whitelist only to exchange addresses

**Result:** AI can trade freely within limits, can't drain wallet

### 2. Treasury Management

**Scenario:** Company treasury with multiple signers

**Rules:**
- Amounts > 10 ETH require approval
- Business hours only (9 AM - 5 PM)
- Blacklist known scam addresses

**Result:** Small payments automatic, large payments reviewed

### 3. Personal Wallet Protection

**Scenario:** Individual user with savings

**Rules:**
- Daily limit: 0.5 ETH
- Max 5 transactions per day
- Time restriction: No transactions midnight-6 AM

**Result:** Protection from hacks, fat-finger mistakes, late-night bad decisions

---

## ✅ Phase 3 Complete!

**What you have:**
- ✅ 6 rule types implemented
- ✅ Automatic enforcement on every transaction
- ✅ Risk scoring and pattern detection
- ✅ Complete audit logging
- ✅ API for rule management
- ✅ Rule templates for common scenarios
- ✅ 6/7 tests passing

**What this enables:**
- 🤖 AI agents can operate autonomously within limits
- 🛡️ Automatic protection from costly mistakes
- 📊 Complete transparency and auditability
- ⚡ No manual checks needed for routine transactions
- 🎯 Fine-grained control over every aspect

**Next:** Phase 4 - AI Natural Language Integration

