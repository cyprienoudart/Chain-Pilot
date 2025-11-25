# 🎬 ChainPilot Demo - Quick Reference Card

**Print this or keep it visible during your demo!**

---

## ⚡ 3-Step Quick Start

```bash
# 1. Setup (5 min)
./setup_demo.sh

# 2. Get funds (10 min)
# Visit: https://sepoliafaucet.com/

# 3. Run demo (2 min)
python3 run.py
python3 verify_demo_setup.py
```

---

## 🎯 Essential Commands

### Create & Load Wallet
```bash
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "demo_wallet"}'

curl -X POST http://localhost:8000/api/v1/wallet/load \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "demo_wallet"}'
```

### Check Balance
```bash
curl http://localhost:8000/api/v1/wallet/balance
```

### Send Transaction (REAL!)
```bash
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{"to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7", "value": 0.01}'
```

### AI Transaction
```bash
# Add name
curl -X POST http://localhost:8000/api/v1/ai/add-name \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"}'

# Send with AI
curl -X POST http://localhost:8000/api/v1/ai/parse \
  -H "Content-Type: application/json" \
  -d '{"text": "Send 0.005 ETH to Alice", "execute": true}'
```

### Security Demo
```bash
# Create spending limit
curl -X POST http://localhost:8000/api/v1/rules/create \
  -H "Content-Type: application/json" \
  -d '{"name": "Demo Limit", "rule_type": "spending_limit", "parameters": {"type": "daily", "amount": 0.05}, "action": "deny", "enabled": true}'

# Try to exceed (will be blocked)
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{"to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7", "value": 0.1}'
```

---

## 🌐 Important URLs

- **Dashboard:** http://localhost:8000/
- **API Docs:** http://localhost:8000/docs
- **Health:** http://localhost:8000/health
- **Sepolia Faucet:** https://sepoliafaucet.com/
- **Etherscan:** https://sepolia.etherscan.io/

---

## 🎤 5-Minute Demo Script

**[0:00-0:30] Opening**
> "ChainPilot lets AI manage crypto with built-in security. Watch this real transaction."

**[0:30-1:30] Send Transaction**
> Execute curl → Show tx_hash → "It's on the blockchain now."

**[1:30-2:30] Dashboard**
> Refresh → Transaction appears → Status: pending → confirmed → Balance decreased

**[2:30-3:30] Etherscan**
> Open link → Show block, gas, confirmations → "Money actually moved!"

**[3:30-4:30] AI Demo**
> "Send 0.005 ETH to Alice" → Parsed → Executed → "Natural language!"

**[4:30-5:00] Security**
> Create limit → Try to exceed → Blocked → "AI can't bypass rules."

---

## ✅ Pre-Demo Checklist

- [ ] Server running: `python3 run.py`
- [ ] Dashboard open: http://localhost:8000/
- [ ] Terminal commands ready
- [ ] Wallet has 0.5+ ETH
- [ ] Etherscan tab open
- [ ] `verify_demo_setup.py` passed

---

## 🐛 Quick Troubleshooting

**Server won't start?**
```bash
pkill -f "python3 run.py"
python3 run.py
```

**No funds?**
- Visit: https://sepoliafaucet.com/
- Wait 30 seconds

**Transaction pending?**
- Wait 1-2 minutes
- Check Etherscan

**Dashboard not updating?**
- Press F5 (refresh)
- Check server logs

---

## 📊 What Success Looks Like

✅ API request sent  
✅ Dashboard shows transaction  
✅ Etherscan confirms on blockchain  
✅ Balance changed  
✅ Security rules enforced  

---

**Quick Help:** See DEMO_GUIDE.md for full walkthrough

