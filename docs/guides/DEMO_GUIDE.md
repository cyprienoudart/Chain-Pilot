# 🎬 ChainPilot Live Demo Guide

**Complete guide for demonstrating ChainPilot with REAL blockchain transactions**

⚠️ **IMPORTANT:** This demo uses REAL blockchain networks. Start with testnet funds!

---

## 🎯 Demo Objectives

Show how ChainPilot:
1. ✅ Receives AI requests via API
2. ✅ Displays them in real-time dashboard
3. ✅ Executes REAL blockchain transactions
4. ✅ Shows changes in your crypto account
5. ✅ Enforces security controls

---

## 📋 Prerequisites

### 1. Get Testnet Funds (FREE)

**Recommended: Sepolia Testnet**

```bash
# Get free Sepolia ETH from faucets:
# 1. https://sepoliafaucet.com/
# 2. https://www.alchemy.com/faucets/ethereum-sepolia
# 3. https://faucet.quicknode.com/ethereum/sepolia

# You'll need:
# - A crypto wallet (MetaMask recommended)
# - Twitter/GitHub account (for faucet verification)
# - 0.5 Sepolia ETH (enough for 10-20 transactions)
```

### 2. Get RPC URL

**Option A: Alchemy (Recommended)**
1. Go to https://www.alchemy.com/
2. Sign up (free)
3. Create a new app (Sepolia network)
4. Copy your HTTP URL: `https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY`

**Option B: Infura**
1. Go to https://infura.io/
2. Sign up (free)
3. Create project
4. Copy Sepolia endpoint: `https://sepolia.infura.io/v3/YOUR_KEY`

### 3. Prepare Two Addresses

- **Your Wallet:** Where you have testnet funds
- **Recipient:** Where you'll send funds (can be another address you control)

---

## 🚀 Setup for Live Demo

### Step 1: Configure Environment

Create `.env` file in project root:

```bash
cd /Users/cyprienoudart/Documents/work/personal/projects/Chain-Pilot

cat > .env << 'EOF'
# Sepolia Testnet Configuration
CHAINPILOT_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_ALCHEMY_KEY
CHAINPILOT_CHAIN_ID=11155111
CHAINPILOT_NETWORK_NAME=sepolia

# Security Configuration
CHAINPILOT_SECURITY_LEVEL=MODERATE  # More permissive for demo
CHAINPILOT_SANDBOX_MODE=false       # REAL transactions!

# Optional: Custom Limits
# CHAINPILOT_MAX_SINGLE_TX=0.1      # 0.1 ETH max per transaction
# CHAINPILOT_HOURLY_LIMIT=0.5       # 0.5 ETH per hour
# CHAINPILOT_DAILY_LIMIT=2.0        # 2.0 ETH per day
EOF

# Replace YOUR_ALCHEMY_KEY with your actual key!
```

### Step 2: Import Your Wallet

You have two options:

**Option A: Create New Wallet in ChainPilot**
```bash
# Start server
python3 run.py

# In another terminal, create wallet
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "demo_wallet"}'

# Load it
curl -X POST http://localhost:8000/api/v1/wallet/load \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "demo_wallet"}'

# Get the address and send testnet ETH to it
```

**Option B: Import Existing Wallet** (Advanced)
```python
# Use Python to import your private key
from src.execution.secure_execution import WalletManager
from src.execution.web3_connection import Web3Manager

# Initialize managers
web3_mgr = Web3Manager()
await web3_mgr.connect()
wallet_mgr = WalletManager(web3_mgr)

# Import wallet (NEVER commit this code!)
private_key = "YOUR_PRIVATE_KEY_HERE"  # From MetaMask: Settings > Security > Show Private Key
wallet_mgr.import_wallet("demo_wallet", private_key, "your_password")
```

### Step 3: Verify Setup

```bash
# Check balance
curl http://localhost:8000/api/v1/wallet/balance

# Should show:
# {
#   "address": "0x...",
#   "balance_wei": "500000000000000000",  # 0.5 ETH in wei
#   "balance_ether": 0.5,
#   "network": "sepolia"
# }
```

---

## 🎬 Demo Script

### Demo Flow: Send 0.01 ETH and Watch It Happen

#### 1. Open Dashboard

```bash
# Terminal 1: Start server (if not already running)
python3 run.py

# Open browser to:
# http://localhost:8000/
```

**Show:**
- Dashboard with current balance
- Transaction history (empty)
- Active rules

#### 2. Send Transaction via API

```bash
# Terminal 2: Send transaction request
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
    "value": 0.01,
    "note": "ChainPilot Demo Transaction"
  }'
```

**Expected Response:**
```json
{
  "tx_hash": "0xabc123...",
  "from_address": "0x...",
  "to_address": "0x742d...",
  "value_ether": 0.01,
  "gas_price_gwei": 2.5,
  "status": "pending",
  "explorer_url": "https://sepolia.etherscan.io/tx/0xabc123..."
}
```

#### 3. Watch Dashboard Update

**Show in dashboard (auto-refreshes every 10s):**
- ✅ New transaction appears in history
- ✅ Balance decreases by 0.01 ETH + gas fees
- ✅ Transaction status changes: pending → confirmed
- ✅ Audit log entry created

#### 4. Verify on Blockchain Explorer

```bash
# Open the explorer URL from the response
# https://sepolia.etherscan.io/tx/0xabc123...
```

**Show:**
- ✅ Transaction confirmed on blockchain
- ✅ Block number and timestamp
- ✅ Gas fees paid
- ✅ From/To addresses match
- ✅ Amount matches (0.01 ETH)

#### 5. Check Recipient Balance

```bash
# Query recipient address
curl http://localhost:8000/api/v1/wallet/balance?address=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7
```

**Show:**
- ✅ Recipient balance increased by 0.01 ETH

---

## 🤖 AI Demo: Natural Language Transaction

### Demo Flow: Use AI to Send ETH

#### 1. Add Name Mapping

```bash
# Map "Alice" to an address
curl -X POST http://localhost:8000/api/v1/ai/add-name \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice",
    "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
  }'
```

#### 2. Send with Natural Language

```bash
# Use AI to parse and execute
curl -X POST http://localhost:8000/api/v1/ai/parse \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Send 0.005 ETH to Alice",
    "execute": true
  }'
```

**Show:**
- ✅ AI parses intent: "send_transaction"
- ✅ Extracts amount: 0.005 ETH
- ✅ Resolves "Alice" to address
- ✅ Executes transaction
- ✅ Returns transaction hash

#### 3. Watch It on Dashboard

**Show:**
- ✅ Transaction appears with note: "AI: Send 0.005 ETH to Alice"
- ✅ Security rules applied
- ✅ Audit log includes AI intent

---

## 🔒 Security Demo: Show Limits Work

### Demo Flow: Try to Exceed Limits

#### 1. Set a Spending Rule

```bash
# Create a daily spending limit
curl -X POST http://localhost:8000/api/v1/rules/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Limit Demo",
    "rule_type": "spending_limit",
    "parameters": {"type": "daily", "amount": 0.05},
    "action": "deny",
    "enabled": true
  }'
```

#### 2. Try to Exceed Limit

```bash
# Send 0.03 ETH (should work)
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{"to_address": "0x742d...", "value": 0.03}'

# Send another 0.03 ETH (should be blocked - total would be 0.06)
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{"to_address": "0x742d...", "value": 0.03}'
```

**Show:**
- ✅ First transaction: Success
- ✅ Second transaction: BLOCKED
- ✅ Error: "Would exceed daily spending limit"
- ✅ Dashboard shows: 1 allowed, 1 denied

---

## 📊 Demo Checklist

Before the demo, verify:

- [ ] Testnet funds in wallet (0.5+ ETH)
- [ ] RPC URL configured and working
- [ ] Server running (no sandbox mode)
- [ ] Dashboard accessible (http://localhost:8000)
- [ ] Test transaction successful
- [ ] Block explorer links work
- [ ] Balance changes visible
- [ ] Have recipient address ready
- [ ] Browser open to dashboard
- [ ] Terminal ready for API calls

---

## 🎤 Demo Script (5 minutes)

### Opening (30 seconds)
"Today I'm showing ChainPilot - an AI-controlled crypto management system with built-in security. Let me show you a real transaction from request to blockchain."

### Part 1: Dashboard (30 seconds)
"Here's the dashboard showing my wallet balance: 0.5 Sepolia ETH. No transactions yet. Now let's send some crypto."

### Part 2: API Request (1 minute)
"I'm sending a request to transfer 0.01 ETH to this address..."
```bash
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -d '{"to_address": "0x742d...", "value": 0.01}'
```
"Got the transaction hash. Notice it's already on the blockchain."

### Part 3: Dashboard Update (1 minute)
"Refreshing the dashboard... see? Transaction appeared. Status: pending. After 15 seconds... confirmed! Balance decreased by 0.01 ETH plus gas."

### Part 4: Blockchain Verification (1 minute)
"Let's verify on Etherscan... here's the transaction. Block number, timestamp, gas fees - all real. The money actually moved."

### Part 5: AI Demo (1 minute)
"Now with AI: 'Send 0.005 ETH to Alice'... parsed the intent, resolved the name, executed the transaction. All with natural language."

### Part 6: Security (30 seconds)
"Security: I set a daily limit of 0.05 ETH. First transaction works... second one blocked. 'Exceeds daily limit.' AI can't bypass these rules."

### Closing (30 seconds)
"That's ChainPilot: AI-controlled crypto with real transactions, real-time dashboard, and unbreakable security rules. From API to blockchain in seconds."

---

## 🎥 Recording Tips

### What to Show

1. **Terminal Window** - API requests and responses
2. **Dashboard Browser** - Real-time updates
3. **Etherscan** - Blockchain verification
4. **Code Editor** (optional) - Show security rules

### Camera Angles

- **Split screen:** Terminal + Dashboard side-by-side
- **Full screen:** Dashboard during updates
- **Picture-in-picture:** Etherscan verification

### What to Highlight

- ✅ Speed (request → blockchain in ~15 seconds)
- ✅ Real-time dashboard updates
- ✅ Actual blockchain transactions
- ✅ Security enforcement
- ✅ Natural language AI

---

## ⚠️ Safety Reminders

### DO
✅ Use testnet (Sepolia) for demos
✅ Start with small amounts (0.01 ETH)
✅ Keep private keys secure
✅ Test everything before live demo
✅ Have backup plan if network is slow

### DON'T
❌ Use mainnet for demos (expensive!)
❌ Expose private keys on screen
❌ Send to unknown addresses
❌ Disable security features
❌ Rush through transactions

---

## 🐛 Troubleshooting

### Transaction Pending Forever
- **Cause:** Low gas price or network congestion
- **Fix:** Wait or increase gas price in config

### "Insufficient Funds" Error
- **Cause:** Not enough ETH for gas
- **Fix:** Get more testnet ETH from faucet

### RPC Connection Failed
- **Cause:** Invalid RPC URL or rate limit
- **Fix:** Check URL, try different RPC provider

### Dashboard Not Updating
- **Cause:** Auto-refresh paused or server issue
- **Fix:** Manual refresh or restart server

---

## 📈 Success Metrics

Your demo is successful if you show:
- ✅ API request received
- ✅ Dashboard displays transaction
- ✅ Blockchain confirms transaction
- ✅ Balance changes visible
- ✅ Security rules enforced

---

## 🎉 After the Demo

### Follow-up Actions
1. Share Etherscan link as proof
2. Show dashboard screenshot with transaction
3. Demonstrate other features (tokens, rules, AI)
4. Q&A about security architecture

### Additional Demos
- ERC-20 token transfers
- Rule engine with multiple rules
- AI chat interface
- Approval workflow
- Rate limiting in action

---

## 📞 Support

**If something goes wrong during demo:**
- Fall back to sandbox mode: `python3 run.py --sandbox`
- Use pre-recorded video as backup
- Have screenshots ready

**For help:**
- Check logs: `tail -f /tmp/chainpilot_server.log`
- Review [TESTING_GUIDE.md](docs/guides/TESTING_GUIDE.md)
- Check [HOW_IT_WORKS.md](docs/technical/HOW_IT_WORKS.md)

---

**Demo Version:** 1.0  
**Last Updated:** November 23, 2025  
**Status:** ✅ Ready for live demonstration

