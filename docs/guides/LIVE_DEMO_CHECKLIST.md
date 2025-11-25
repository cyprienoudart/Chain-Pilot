# 🎬 Live Demo Checklist

**Pre-Demo Setup for Real Blockchain Transactions**

---

## ✅ Setup Phase

### 1. Configuration (5 minutes)
- [ ] Run `./setup_demo.sh`
- [ ] Choose network (Sepolia recommended)
- [ ] Enter RPC URL (Alchemy/Infura)
- [ ] Select security level (MODERATE for demos)
- [ ] Verify `.env` file created

### 2. Get Testnet Funds (10 minutes)
- [ ] Visit faucet: https://sepoliafaucet.com/
- [ ] Connect wallet (MetaMask)
- [ ] Request 0.5 Sepolia ETH
- [ ] Wait for confirmation (~30 seconds)
- [ ] Verify funds received

### 3. Wallet Setup (2 minutes)
- [ ] Start server: `python3 run.py`
- [ ] Create wallet OR import existing
- [ ] Load wallet
- [ ] Check balance > 0.01 ETH
- [ ] Note your wallet address

### 4. Verification (1 minute)
- [ ] Run `python3 verify_demo_setup.py`
- [ ] All checks pass ✅
- [ ] Dashboard accessible
- [ ] Wallet has funds

---

## 🎬 Demo Execution

### Preparation (Before Demo)
- [ ] Server running: `python3 run.py`
- [ ] Dashboard open: http://localhost:8000/
- [ ] API docs open: http://localhost:8000/docs
- [ ] Terminal ready for commands
- [ ] Browser window visible
- [ ] Etherscan tab ready

### Demo Flow (5 minutes)

#### Part 1: Show Dashboard (30 sec)
- [ ] Show current balance
- [ ] Show empty transaction history
- [ ] Point out AI chat interface

#### Part 2: Send Transaction (1 min)
```bash
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{"to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7", "value": 0.01}'
```
- [ ] Copy command
- [ ] Execute in terminal
- [ ] Show response (tx_hash)
- [ ] Copy Etherscan URL

#### Part 3: Dashboard Update (1 min)
- [ ] Show transaction appearing
- [ ] Show status: pending → confirmed
- [ ] Show balance decrease
- [ ] Point out gas fees

#### Part 4: Blockchain Verification (1 min)
- [ ] Open Etherscan link
- [ ] Show transaction details
- [ ] Show block number
- [ ] Show gas fees
- [ ] Show confirmations

#### Part 5: AI Demo (1 min)
```bash
# Add name mapping
curl -X POST http://localhost:8000/api/v1/ai/add-name \
  -d '{"name": "Alice", "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"}'

# Send with AI
curl -X POST http://localhost:8000/api/v1/ai/parse \
  -d '{"text": "Send 0.005 ETH to Alice", "execute": true}'
```
- [ ] Show AI parsing
- [ ] Show execution
- [ ] Show dashboard update

#### Part 6: Security Demo (30 sec)
```bash
# Create spending limit
curl -X POST http://localhost:8000/api/v1/rules/create \
  -d '{"name": "Demo Limit", "rule_type": "spending_limit", "parameters": {"type": "daily", "amount": 0.05}, "action": "deny", "enabled": true}'

# Try to exceed (should fail)
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -d '{"to_address": "0x742d...", "value": 0.1}'
```
- [ ] Show limit creation
- [ ] Show transaction blocked
- [ ] Explain security

---

## 📋 Pre-Demo Command Checklist

**Have these ready in terminals:**

### Terminal 1: Basic Transaction
```bash
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{"to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7", "value": 0.01}'
```

### Terminal 2: AI Transaction
```bash
curl -X POST http://localhost:8000/api/v1/ai/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "Send 0.005 ETH to Alice", "execute": true}'
```

### Terminal 3: Check Balance
```bash
curl http://localhost:8000/api/v1/wallet/balance
```

### Terminal 4: Create Rule
```bash
curl -X POST http://localhost:8000/api/v1/rules/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Demo Limit", "rule_type": "spending_limit", "parameters": {"type": "daily", "amount": 0.05}, "action": "deny", "enabled": true}'
```

---

## 🎤 Demo Script (Talking Points)

### Opening
"ChainPilot lets AI agents manage cryptocurrency with built-in security. I'll show you a real transaction from API request to blockchain confirmation."

### Dashboard
"Here's our dashboard - current balance is 0.5 Sepolia ETH on the testnet. No transactions yet. Let's change that."

### Transaction
"I'm sending an API request to transfer 0.01 ETH... and we got a transaction hash. This is now on the blockchain."

### Verification
"Refreshing the dashboard... there it is! Status pending... and now confirmed. Balance decreased. Let's verify on Etherscan..."

### Blockchain
"Here's the actual transaction on the Ethereum blockchain. Block number, timestamp, gas fees - all real. The money actually moved."

### AI
"Now with AI: I'll just say 'Send 0.005 ETH to Alice' and... it parsed my intent, resolved the name, and executed. No coding needed."

### Security
"Security: I set a daily spending limit of 0.05 ETH. First transaction works... second one blocked. 'Exceeds limit.' The AI can't bypass these rules."

### Closing
"That's ChainPilot: AI-controlled crypto with real transactions, real-time monitoring, and unbreakable security. From API to blockchain in seconds."

---

## ⚠️ Troubleshooting

### Transaction Stuck as Pending
- **Cause**: Low gas price or network congestion
- **Fix**: Wait 1-2 minutes or check gas settings

### RPC Error
- **Cause**: Rate limit or invalid URL
- **Fix**: Try different RPC provider

### Insufficient Funds
- **Cause**: Not enough ETH for gas
- **Fix**: Get more from faucet

### Dashboard Not Updating
- **Cause**: Auto-refresh paused
- **Fix**: Manual refresh (F5)

---

## 📊 Success Criteria

Demo is successful if you show:
- ✅ API request sent
- ✅ Dashboard displays transaction
- ✅ Blockchain confirms transaction
- ✅ Balance changes visible
- ✅ Security rules enforced

---

## 🎯 After Demo

### Follow-up
- Share Etherscan link as proof
- Show code on GitHub
- Offer to answer questions
- Provide documentation links

### Cleanup
- Stop server: Ctrl+C
- Save wallet files
- Document any issues
- Plan improvements

---

**Last Updated:** November 23, 2025  
**Demo Ready:** ✅ YES
