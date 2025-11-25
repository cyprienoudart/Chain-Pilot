# ChainPilot API Documentation

Complete API reference for ChainPilot v1.0.0

**Base URL**: `http://localhost:8000/api/v1`  
**Interactive Docs**: `http://localhost:8000/docs`  
**Content-Type**: `application/json`

---

## Table of Contents

- [Authentication](#authentication)
- [Wallet Management](#wallet-management)
- [Transactions](#transactions)
- [Token Operations](#token-operations)
- [Rule Management](#rule-management)
- [AI Natural Language](#ai-natural-language)
- [Audit & History](#audit--history)
- [Network Information](#network-information)
- [Health & Status](#health--status)
- [Error Handling](#error-handling)

---

## Authentication

### API Key (Optional)

If `CHAINPILOT_API_KEY` environment variable is set, include it in requests:

```http
X-API-Key: your-secret-api-key
```

**Example**:
```bash
curl -H "X-API-Key: your-secret-api-key" \
  http://localhost:8000/api/v1/wallet/list
```

---

## Wallet Management

### Create Wallet

Create a new wallet with encrypted private key storage.

**Endpoint**: `POST /wallet/create`

**Request Body**:
```json
{
  "wallet_name": "my_wallet"
}
```

**Response** (200):
```json
{
  "wallet_name": "my_wallet",
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "network": "sepolia"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "my_wallet"}'
```

---

### Load Wallet

Load an existing wallet for use in transactions.

**Endpoint**: `POST /wallet/load`

**Request Body**:
```json
{
  "wallet_name": "my_wallet"
}
```

**Response** (200):
```json
{
  "message": "Wallet loaded successfully",
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "network": "sepolia"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/wallet/load \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "my_wallet"}'
```

---

### List Wallets

Get all available wallets.

**Endpoint**: `GET /wallet/list`

**Response** (200):
```json
[
  {
    "name": "my_wallet",
    "address": "0x1234567890abcdef1234567890abcdef12345678",
    "network": "sepolia"
  },
  {
    "name": "another_wallet",
    "address": "0xabcdef1234567890abcdef1234567890abcdef12",
    "network": "mainnet"
  }
]
```

**Example**:
```bash
curl http://localhost:8000/api/v1/wallet/list
```

---

### Get Balance

Get balance for current wallet or specific address.

**Endpoint**: `GET /wallet/balance`

**Query Parameters**:
- `address` (optional): Specific address to check

**Response** (200):
```json
{
  "address": "0x1234567890abcdef1234567890abcdef12345678",
  "balance_wei": "1000000000000000000",
  "balance_ether": 1.0,
  "currency": "ETH",
  "network": "sepolia"
}
```

**Example**:
```bash
# Current wallet
curl http://localhost:8000/api/v1/wallet/balance

# Specific address
curl "http://localhost:8000/api/v1/wallet/balance?address=0x1234..."
```

---

## Transactions

### Send Transaction

Send native currency (ETH) to an address.

**Endpoint**: `POST /transaction/send`

**Request Body**:
```json
{
  "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
  "value": 0.01
}
```

**Response** (200):
```json
{
  "tx_hash": "0xabc123...",
  "from_address": "0x1234...",
  "to_address": "0x742d...",
  "value": "0.01",
  "status": "confirmed",
  "gas_used": 21000
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
    "value": 0.01
  }'
```

---

### Estimate Gas

Estimate gas for a transaction.

**Endpoint**: `POST /transaction/estimate-gas`

**Request Body**:
```json
{
  "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
  "value": 0.01
}
```

**Response** (200):
```json
{
  "gas_limit": 21000,
  "gas_price_gwei": 20,
  "estimated_cost_eth": 0.00042,
  "max_fee_eth": 0.001
}
```

---

### Get Transaction Status

Get status of a transaction by hash.

**Endpoint**: `GET /transaction/{tx_hash}`

**Response** (200):
```json
{
  "tx_hash": "0xabc123...",
  "status": "confirmed",
  "block_number": 12345678,
  "from_address": "0x1234...",
  "to_address": "0x742d...",
  "value": "0.01",
  "gas_used": 21000
}
```

**Example**:
```bash
curl http://localhost:8000/api/v1/transaction/0xabc123...
```

---

## Token Operations

### Transfer ERC-20 Token

Transfer ERC-20 tokens to an address.

**Endpoint**: `POST /token/transfer`

**Request Body**:
```json
{
  "token_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
  "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
  "amount": 100.0
}
```

**Response** (200):
```json
{
  "tx_hash": "0xdef456...",
  "token_address": "0x6B17...",
  "token_symbol": "DAI",
  "from_address": "0x1234...",
  "to_address": "0x742d...",
  "amount": "100.0",
  "status": "confirmed"
}
```

---

### Get Token Balance

Get ERC-20 token balance.

**Endpoint**: `GET /token/balance`

**Query Parameters**:
- `token_address` (required): Token contract address
- `address` (optional): Specific address to check

**Response** (200):
```json
{
  "token_address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
  "token_symbol": "DAI",
  "token_name": "Dai Stablecoin",
  "balance": "1000.0",
  "decimals": 18
}
```

---

## Rule Management

### Create Rule

Create a new automated rule.

**Endpoint**: `POST /rules/create`

**Request Body**:
```json
{
  "rule_type": "spending_limit",
  "rule_name": "Daily Limit",
  "parameters": {
    "type": "daily",
    "amount": 1.0
  },
  "action": "deny",
  "enabled": true,
  "priority": 5
}
```

**Rule Types**:
- `spending_limit`: Limit spending per period
- `address_whitelist`: Only allow specific addresses
- `address_blacklist`: Block specific addresses
- `time_restriction`: Limit by time of day
- `amount_threshold`: Require approval above amount
- `daily_transaction_count`: Limit transaction frequency

**Actions**:
- `allow`: Explicitly allow (override other rules)
- `deny`: Block transaction
- `require_approval`: Flag for manual approval

**Response** (200):
```json
{
  "message": "Rule created successfully",
  "rule_id": 1,
  "rule_name": "Daily Limit",
  "rule_type": "spending_limit",
  "enabled": true
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/v1/rules/create \
  -H "Content-Type: application/json" \
  -d '{
    "rule_type": "spending_limit",
    "rule_name": "Daily Limit",
    "parameters": {"type": "daily", "amount": 1.0},
    "action": "deny",
    "enabled": true,
    "priority": 5
  }'
```

---

### Get All Rules

Get all rules (enabled and disabled).

**Endpoint**: `GET /rules`

**Query Parameters**:
- `enabled_only` (optional): Only return enabled rules

**Response** (200):
```json
{
  "message": "Rules retrieved",
  "count": 2,
  "rules": [
    {
      "rule_id": 1,
      "rule_type": "spending_limit",
      "rule_name": "Daily Limit",
      "parameters": {"type": "daily", "amount": 1.0},
      "action": "deny",
      "enabled": true,
      "priority": 5
    }
  ]
}
```

---

### Update Rule

Update an existing rule.

**Endpoint**: `PUT /rules/{rule_id}`

**Request Body**:
```json
{
  "enabled": false,
  "parameters": {"type": "daily", "amount": 2.0},
  "priority": 10
}
```

**Response** (200):
```json
{
  "message": "Rule updated successfully",
  "rule_id": 1
}
```

---

### Delete Rule

Delete a rule.

**Endpoint**: `DELETE /rules/{rule_id}`

**Response** (200):
```json
{
  "message": "Rule deleted successfully",
  "rule_id": 1
}
```

---

### Evaluate Transaction

Evaluate a transaction against all rules WITHOUT executing it.

**Endpoint**: `POST /rules/evaluate`

**Request Body**:
```json
{
  "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
  "value": 0.5,
  "from_address": "0x1234..."
}
```

**Response** (200):
```json
{
  "message": "Transaction evaluated",
  "transaction": {
    "from_address": "0x1234...",
    "to_address": "0x742d...",
    "value": 0.5
  },
  "allowed": false,
  "action": "deny",
  "risk_level": "high",
  "failed_rules": [
    {
      "rule_id": 1,
      "rule_name": "Daily Limit",
      "reason": "Would exceed daily limit"
    }
  ]
}
```

---

### Get Rule Templates

Get pre-configured rule templates.

**Endpoint**: `GET /rules/templates`

**Response** (200):
```json
{
  "message": "Rule templates retrieved",
  "count": 6,
  "templates": [
    {
      "name": "Daily Spending Limit (1 ETH)",
      "description": "Block transactions that would exceed 1 ETH per day",
      "rule_type": "spending_limit",
      "parameters": {"type": "daily", "amount": 1.0},
      "action": "deny"
    }
  ]
}
```

---

## AI Natural Language

### Parse Intent

Parse natural language text into structured transaction intent.

**Endpoint**: `POST /ai/parse`

**Request Body**:
```json
{
  "text": "Send 0.5 ETH to alice",
  "execute": false
}
```

**Response** (200):
```json
{
  "intent": "send_transaction",
  "confidence": 0.95,
  "entities": {
    "amount": 0.5,
    "currency": "ETH",
    "recipient": "alice",
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
  },
  "action_status": "parsed",
  "requires_approval": false
}
```

**With Execution** (`execute: true`):
```json
{
  "intent": "send_transaction",
  "confidence": 0.95,
  "entities": {...},
  "action_status": "executed",
  "tx_hash": "0xabc123...",
  "result": {...}
}
```

**Example**:
```bash
# Parse only
curl -X POST http://localhost:8000/api/v1/ai/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "What is my balance?", "execute": false}'

# Parse and execute
curl -X POST http://localhost:8000/api/v1/ai/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "Send 0.5 ETH to alice", "execute": true}'
```

---

### Add Name Mapping

Map a friendly name to an address for use in NL commands.

**Endpoint**: `POST /ai/add-name`

**Request Body**:
```json
{
  "name": "alice",
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
}
```

**Response** (200):
```json
{
  "message": "Name mapping added",
  "name": "alice",
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
}
```

---

### Get Examples

Get example natural language commands.

**Endpoint**: `GET /ai/examples`

**Response** (200):
```json
{
  "check_balance": [
    "What is my balance?",
    "How much ETH do I have?"
  ],
  "send_transaction": [
    "Send 0.5 ETH to alice",
    "Transfer 100 DAI to 0x742d..."
  ],
  "create_rule": [
    "Create a daily spending limit of 1 ETH",
    "Block transactions to 0xabc..."
  ]
}
```

---

## Audit & History

### Get Transactions

Get transaction history from audit log.

**Endpoint**: `GET /audit/transactions`

**Query Parameters**:
- `limit` (optional): Max number of transactions (default: 50)
- `offset` (optional): Pagination offset (default: 0)
- `address` (optional): Filter by address
- `status` (optional): Filter by status

**Response** (200):
```json
{
  "message": "Transactions retrieved",
  "count": 2,
  "transactions": [
    {
      "tx_hash": "0xabc123...",
      "from_address": "0x1234...",
      "to_address": "0x742d...",
      "value": "0.01",
      "value_ether": 0.01,
      "status": "confirmed",
      "gas_used": 21000,
      "timestamp": "2025-11-24T12:00:00"
    }
  ]
}
```

**Example**:
```bash
# Get last 10 transactions
curl "http://localhost:8000/api/v1/audit/transactions?limit=10"

# Get transactions for specific address
curl "http://localhost:8000/api/v1/audit/transactions?address=0x1234..."

# Get confirmed transactions only
curl "http://localhost:8000/api/v1/audit/transactions?status=confirmed"
```

---

## Network Information

### Get Network Info

Get current network information.

**Endpoint**: `GET /network/info`

**Response** (200):
```json
{
  "name": "Sepolia Testnet",
  "chain_id": 11155111,
  "currency": "ETH",
  "explorer": "https://sepolia.etherscan.io",
  "block_number": 12345678,
  "gas_price": 20000000000,
  "status": "connected"
}
```

---

## Health & Status

### Health Check

Check server health and connectivity.

**Endpoint**: `GET /health`

**Response** (200):
```json
{
  "status": "healthy",
  "web3_connected": true,
  "network": {
    "name": "Sepolia Testnet",
    "chain_id": 11155111,
    "block_number": 12345678
  },
  "sandbox_mode": false,
  "security_level": "strict",
  "rate_limiting_enabled": true,
  "api_auth_enabled": false
}
```

---

### Root Status

Get API status and version.

**Endpoint**: `GET /`

**Response** (200):
```json
{
  "name": "ChainPilot API",
  "version": "1.0.0",
  "status": "running",
  "phase": "Production Ready"
}
```

---

## Error Handling

### Error Response Format

All errors return a consistent format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Missing or invalid API key |
| 403 | Forbidden | Access denied (rules, AI controls) |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Common Error Examples

**Validation Error** (422):
```json
{
  "detail": [
    {
      "loc": ["body", "value"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Rule Denial** (403):
```json
{
  "detail": {
    "message": "Transaction denied by rules",
    "reason": "Would exceed daily spending limit",
    "risk_level": "high",
    "failed_rules": [...]
  }
}
```

**Rate Limit** (429):
```json
{
  "detail": "Rate limit exceeded. Please try again later."
}
```

---

## Rate Limiting

**Default Limits**:
- 100 requests per 60 seconds per IP/API key
- Configurable per endpoint
- Uses token bucket algorithm

**Headers**:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1637123456
```

---

## Best Practices

1. **Always handle errors**: Check response status and handle errors gracefully
2. **Use appropriate limits**: Set sensible values for pagination and queries
3. **Cache when possible**: Cache network info, rule templates, etc.
4. **Test with sandbox mode**: Use `--sandbox` flag for development
5. **Monitor rate limits**: Check remaining requests in headers
6. **Validate inputs**: Ensure addresses are valid checksummed format
7. **Use transactions**: For database consistency
8. **Log everything**: Enable comprehensive logging for debugging

---

## Examples

### Complete Workflow

```bash
# 1. Create wallet
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "my_wallet"}'

# 2. Load wallet
curl -X POST http://localhost:8000/api/v1/wallet/load \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "my_wallet"}'

# 3. Check balance
curl http://localhost:8000/api/v1/wallet/balance

# 4. Create a rule
curl -X POST http://localhost:8000/api/v1/rules/create \
  -H "Content-Type: application/json" \
  -d '{
    "rule_type": "spending_limit",
    "rule_name": "Daily Limit",
    "parameters": {"type": "daily", "amount": 1.0},
    "action": "deny",
    "enabled": true,
    "priority": 5
  }'

# 5. Send transaction
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
    "value": 0.01
  }'

# 6. Check transaction history
curl "http://localhost:8000/api/v1/audit/transactions?limit=10"
```

---

**Last Updated**: November 24, 2025  
**API Version**: 1.0.0  
**Interactive Docs**: http://localhost:8000/docs

