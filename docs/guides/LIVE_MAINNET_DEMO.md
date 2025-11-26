# 🔴 Live Mainnet Demo Guide

**⚠️ WARNING: This guide uses REAL MONEY on live blockchain networks**

This guide will help you perform a live demo with actual cryptocurrency transactions.

---

## 🚨 Critical Safety Information

### Before You Start

**READ THIS CAREFULLY:**

1. **This uses REAL MONEY**: Transactions cannot be reversed
2. **Gas fees are REAL**: Each transaction costs money
3. **Test first**: Always test on testnet before mainnet
4. **Start small**: Use tiny amounts ($1-5 worth)
5. **Double-check addresses**: One wrong character = lost funds
6. **Have a backup**: Keep recovery phrases secure

### Recommended Networks by Cost

| Network | Gas Cost | Speed | Best For |
|---------|----------|-------|----------|
| **Polygon** | ~$0.001-0.01 | Fast (2s) | ✅ **RECOMMENDED for demos** |
| Arbitrum | ~$0.10-0.50 | Fast (1s) | Good for demos |
| Optimism | ~$0.10-0.50 | Fast (2s) | Good for demos |
| Base | ~$0.10-0.50 | Fast (2s) | Good for demos |
| Ethereum | ~$2-50 | Medium (12s) | ❌ Too expensive for demos |

**💡 Use Polygon for demos - it's real money but costs pennies!**

---

## 📋 Pre-Demo Checklist

### 1. Get Real Funds (~$10-20)

#### Option A: Buy on Exchange (Recommended)
1. **Coinbase/Binance/Kraken**: Buy ETH or MATIC
2. **Withdraw to your wallet**: Note the network (Ethereum/Polygon)
3. **Wait for confirmation**: Usually 10-30 minutes

#### Option B: Bridge from Testnet (Advanced)
- Not recommended - just buy a small amount

### 2. Setup RPC Provider

**Get a free RPC endpoint:**

**Alchemy** (Recommended):
1. Go to [alchemy.com](https://alchemy.com)
2. Sign up (free)
3. Create new app:
   - Name: "ChainPilot Demo"
   - Chain: **Polygon Mainnet** (recommended)
   - Network: Mainnet
4. Copy your API key: `https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY`

**Infura**:
1. Go to [infura.io](https://infura.io)
2. Sign up (free)
3. Create project
4. Select network: Polygon Mainnet
5. Copy endpoint URL

### 3. Configure Environment

Create `.env` file in project root:

```bash
# For Polygon Mainnet (RECOMMENDED)
WEB3_RPC_URL="https://polygon-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
CHAINPILOT_API_KEY="your-secret-key-123"  # Optional

# For Ethereum Mainnet (EXPENSIVE - NOT RECOMMENDED)
# WEB3_RPC_URL="https://mainnet.infura.io/v3/YOUR_PROJECT_ID"

# For Arbitrum (Good alternative)
# WEB3_RPC_URL="https://arb-mainnet.g.alchemy.com/v2/YOUR_API_KEY"
```

### 4. Verify Connection

```bash
# Activate environment
source .venv/bin/activate

# Start server (NOT sandbox mode)
python3 run.py

# Check health
curl http://localhost:8000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "web3_connected": true,
  "network": {
    "name": "Polygon Mainnet",
    "chain_id": 137,
    "block_number": 51234567
  },
  "sandbox_mode": false  // ← Must be false!
}
```

---

## 🎬 Demo Script (10 minutes)

### Part 1: Setup (2 minutes)

**1. Create or Import Wallet**

```bash
# Option A: Create new wallet
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "demo_wallet"}'
```

**Save the response - this is your new wallet address!**

**2. Fund the Wallet**

Transfer $5-10 worth of MATIC (or ETH) to the wallet address from your exchange or MetaMask.

**Wait for confirmation** (~30 seconds on Polygon)

**3. Load Wallet**

```bash
curl -X POST http://localhost:8000/api/v1/wallet/load \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "demo_wallet"}'
```

**4. Verify Balance**

```bash
curl http://localhost:8000/api/v1/wallet/balance
```

**Expected:**
```json
{
  "address": "0x1234...",
  "balance_ether": 5.0,
  "currency": "MATIC",  // or ETH
  "network": "Polygon Mainnet"
}
```

---

### Part 2: Setup Rules (2 minutes)

**1. Create Daily Spending Limit**

```bash
curl -X POST http://localhost:8000/api/v1/rules/create \
  -H "Content-Type: application/json" \
  -d '{
    "rule_type": "spending_limit",
    "rule_name": "Demo Daily Limit",
    "parameters": {"type": "daily", "amount": 1.0},
    "action": "deny",
    "enabled": true,
    "priority": 5
  }'
```

**2. Create Large Transaction Approval**

```bash
curl -X POST http://localhost:8000/api/v1/rules/create \
  -H "Content-Type: application/json" \
  -d '{
    "rule_type": "amount_threshold",
    "rule_name": "Demo Approval Threshold",
    "parameters": {"threshold": 0.5},
    "action": "require_approval",
    "enabled": true,
    "priority": 10
  }'
```

**3. Show Rules in Dashboard**

Open: http://localhost:8000/
- Navigate to "Rules" section
- Show the rules you just created
- Toggle one on/off to demonstrate

---

### Part 3: Send Real Transaction (3 minutes)

**⚠️ THIS WILL SPEND REAL MONEY**

**1. Small Test Transaction (0.01 MATIC ≈ $0.01)**

```bash
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
    "value": 0.01
  }'
```

**2. Show Transaction in Dashboard**

- Refresh dashboard
- See transaction appear in "Recent Transactions"
- Show transaction hash

**3. Verify on Blockchain Explorer**

**Polygon**: https://polygonscan.com/tx/TX_HASH
**Ethereum**: https://etherscan.io/tx/TX_HASH

**Show:**
- Transaction confirmed
- From/To addresses
- Amount sent
- Gas fee paid
- Timestamp

**4. Check Updated Balance**

```bash
curl http://localhost:8000/api/v1/wallet/balance
```

**Show balance decreased by (amount + gas fee)**

---

### Part 4: AI Natural Language (2 minutes)

**1. Add Name Mapping**

```bash
curl -X POST http://localhost:8000/api/v1/ai/add-name \
  -H "Content-Type: application/json" \
  -d '{
    "name": "demo_recipient",
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
  }'
```

**2. Send with AI (Real Money!)**

```bash
curl -X POST http://localhost:8000/api/v1/ai/parse \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Send 0.01 MATIC to demo_recipient",
    "execute": true
  }'
```

**3. Show AI Chat in Dashboard**

- Open dashboard
- Navigate to "AI Assistant"
- Type: "What is my balance?"
- Show AI response with real balance

---

### Part 5: Rule Enforcement (1 minute)

**1. Try to Exceed Daily Limit**

```bash
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
    "value": 2.0
  }'
```

**Expected: 403 Forbidden**
```json
{
  "detail": {
    "message": "Transaction denied by rules",
    "reason": "Would exceed daily spending limit",
    "risk_level": "high"
  }
}
```

**Show in dashboard that transaction was blocked**

---

## 📊 Demo Talking Points

### Security Features
- "All transactions are protected by rules you configure"
- "AI has spending limits - can't drain your wallet"
- "Everything is logged for audit trail"
- "Rules can be toggled on/off instantly"

### AI Integration
- "Natural language: 'send 0.1 ETH to alice' just works"
- "AI understands context and amounts"
- "Subject to all the same rules and limits"

### Dashboard
- "Real-time monitoring of all transactions"
- "Manage rules visually - no code needed"
- "See wallet balances and transaction history"
- "Interactive charts show activity patterns"

### Cost Comparison
- "On Polygon: Gas fees are ~$0.001 per transaction"
- "Same transaction on Ethereum: $5-50"
- "Perfect for high-frequency AI agents"

---

## 🛑 After Demo Cleanup

### 1. Stop Server

```bash
# Press Ctrl+C in terminal
```

### 2. Withdraw Remaining Funds

```bash
# Send remaining balance back to your main wallet
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_address": "YOUR_MAIN_WALLET_ADDRESS",
    "value": 4.5
  }'
```

### 3. Clean Up (Optional)

```bash
# Delete demo wallet files
rm wallets/demo_wallet.json.enc

# Clear database
rm chainpilot.db

# Or just keep them for next demo
```

---

## ⚠️ Troubleshooting

### "Insufficient funds for gas"
- Add more funds to wallet
- Check you're on the right network
- Polygon needs MATIC, not ETH

### "Transaction reverted"
- Check recipient address is valid
- Ensure you have enough balance
- Try lower amount

### "RPC connection failed"
- Verify your RPC URL is correct
- Check internet connection
- Try a different RPC provider

### "Nonce too low"
- Restart the server
- Clear any pending transactions

---

## 💰 Cost Breakdown

### Polygon Mainnet (Recommended)
- **Gas per transaction**: ~$0.001-0.01
- **10 demo transactions**: ~$0.10
- **Total demo cost**: ~$0.20 (with transfers)

### Ethereum Mainnet (Not Recommended)
- **Gas per transaction**: ~$2-50
- **10 demo transactions**: ~$50-200
- **Total demo cost**: $50-300

### Arbitrum/Optimism/Base
- **Gas per transaction**: ~$0.10-0.50
- **10 demo transactions**: ~$2-5
- **Total demo cost**: ~$5-10

---

## 🎯 Demo Success Checklist

After demo, verify:

- ✅ All transactions visible in dashboard
- ✅ Rules successfully blocked high-value transaction
- ✅ AI natural language worked
- ✅ Transactions confirmed on blockchain explorer
- ✅ Balance updated correctly
- ✅ Audit log shows all activity
- ✅ No errors or warnings

---

## 📝 Demo Notes Template

Use this to track your demo:

```
Demo Date: ___________
Network: Polygon Mainnet
Starting Balance: _____ MATIC
Ending Balance: _____ MATIC

Transactions:
1. [TX_HASH] - 0.01 MATIC - Success
2. [TX_HASH] - 0.01 MATIC - Success
3. [Blocked] - 2.0 MATIC - Denied by rules

Total Gas Spent: _____ MATIC (~$_____)
Total Demo Cost: ~$_____

Issues Encountered:
- None / [List any issues]

Audience Feedback:
- [Notes]
```

---

## 🚀 Advanced Demo Ideas

### For Technical Audiences

1. **Show API Documentation**: http://localhost:8000/docs
2. **Live Code Integration**: Show Python script using the API
3. **Rule Evaluation**: Test transaction without executing
4. **Audit Trail**: Show complete transaction history in database

### For Business Audiences

1. **Cost Savings**: Compare Ethereum vs Polygon gas fees
2. **Security Controls**: Emphasize AI spending limits
3. **Compliance**: Show audit trail and rule enforcement
4. **Integration**: Discuss API-first design

### For Investors

1. **Market Size**: Potential for AI-driven DeFi
2. **Security Features**: Compare to competitors
3. **Scalability**: Polygon handles 1000s TPS
4. **Revenue Model**: API usage, enterprise features

---

## 📞 Emergency Contacts

If something goes wrong during demo:

- **RPC Issues**: Switch to backup provider (Infura/Alchemy)
- **Funds Stuck**: Check on explorer, wait for confirmation
- **Server Crash**: Restart with `python3 run.py`
- **Wrong Network**: Check `.env` file

---

## ✅ Pre-Demo Testing Script

Run this 24 hours before your demo:

```bash
# 1. Test connection
curl http://localhost:8000/health

# 2. Test wallet creation
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "test_demo"}'

# 3. Test balance query
curl http://localhost:8000/api/v1/wallet/balance

# 4. Test rule creation
curl -X POST http://localhost:8000/api/v1/rules/create \
  -H "Content-Type: application/json" \
  -d '{
    "rule_type": "spending_limit",
    "rule_name": "Test",
    "parameters": {"type": "daily", "amount": 1.0},
    "action": "deny",
    "enabled": true
  }'

# 5. Test dashboard
open http://localhost:8000/

# All working? You're ready!
```

---

**Last Updated**: November 24, 2025  
**Tested Networks**: Polygon Mainnet, Arbitrum, Optimism  
**Recommended Budget**: $10-20 for full demo

