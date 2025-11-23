# ⚡ Quick Test - 60 Seconds

Get ChainPilot Phase 2 running in under a minute!

## Option 1: Automated Test (Recommended)

```bash
# Terminal 1: Start server
python3 run.py --sandbox

# Terminal 2: Run tests
python3 test_phase2.py
```

**Expected:** All 9 tests pass ✅

---

## Option 2: Manual Test (Interactive)

```bash
# Start server
python3 run.py --sandbox

# Open browser
open http://localhost:8000/docs
```

**Try these 3 endpoints:**

1. **Create Wallet**
   - `POST /api/v1/wallet/create`
   - Body: `{"wallet_name": "test"}`
   - ✅ Get wallet address

2. **Check Balance**
   - `GET /api/v1/wallet/balance`
   - ✅ See 100 ETH

3. **Send Transaction**
   - `POST /api/v1/transaction/send`
   - Body:
   ```json
   {
     "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
     "value": 0.1
   }
   ```
   - ✅ Get transaction hash

**Done!** Phase 2 is working! 🎉

---

## What's Sandbox Mode?

🏖️ **Sandbox = Safe Testing**

- ✅ All transactions simulated
- ✅ No real blockchain needed
- ✅ No testnet funds needed
- ✅ Instant confirmations
- ✅ Pre-loaded with 100 ETH

Perfect for development and testing!

---

## Next Steps

- **Full testing guide:** `TESTING_GUIDE.md`
- **How it works:** `PHASE2_EXPLAINED.md`
- **Technical details:** `PHASE2_SUMMARY.md`

---

## Real Testnet (After Sandbox)

```bash
# 1. Get testnet funds
open https://sepoliafaucet.com

# 2. Start in live mode
python3 run.py

# 3. Send real transaction
# (Use API docs at /docs)
```

---

## Troubleshooting

**Server won't start?**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

**Need help?** Check `TESTING_GUIDE.md`

---

**Quick start:** `python3 run.py --sandbox` + `python3 test_phase2.py` 🚀

