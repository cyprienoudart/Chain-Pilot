# 🧪 ChainPilot Testing Guide

## 🏖️ Sandbox Mode (Recommended for First Test)

Sandbox mode lets you test **everything** without needing testnet funds or real blockchain interaction. Perfect for development and testing!

### What Sandbox Mode Does

✅ **Simulates** all blockchain operations  
✅ **No real transactions** - completely safe  
✅ **No RPC needed** - works offline  
✅ **Instant confirmation** - no waiting  
✅ **Pre-loaded balances** - 100 ETH + 1000 tokens  
✅ **Full database logging** - tracks everything  

---

## 🚀 Quick Start (3 Steps)

### 1. Start Server in Sandbox Mode

```bash
python3 run.py --sandbox
```

You'll see:
```
🏖️  SANDBOX MODE ENABLED
   - Transactions will be simulated
   - No real blockchain interaction
   - Perfect for testing without funds

🚀 Starting ChainPilot API...
📚 Docs will be at: http://localhost:8000/docs
⚠️  SANDBOX: All transactions are simulated
```

### 2. Run Automated Tests

Open a **NEW terminal** (keep server running):

```bash
# Activate virtual environment
source .venv/bin/activate

# Run comprehensive test suite
python3 test_phase2.py
```

### 3. Try Interactive Testing

Visit: **http://localhost:8000/docs**

Try these endpoints:
1. `POST /api/v1/wallet/create` - Create wallet
2. `GET /api/v1/wallet/balance` - See your 100 ETH
3. `POST /api/v1/transaction/estimate` - Estimate a transaction
4. `POST /api/v1/transaction/send` - Send simulated transaction
5. `GET /api/v1/audit/transactions` - View history

---

## 🧪 Automated Test Script

The `test_phase2.py` script runs **9 comprehensive tests**:

### Tests Included

1. **API Health Check** - Verify server is running
2. **Wallet Creation** - Create/load test wallet
3. **Balance Check** - Query wallet balance
4. **Transaction Estimation** - Estimate gas costs
5. **Send Transaction** - Execute simulated transaction
6. **Transaction Status** - Check confirmation
7. **Token Balance** - Query ERC-20 tokens
8. **Audit History** - View transaction logs
9. **Network Info** - Get network details

### Running Tests

```bash
# Make sure server is running first
python3 run.py --sandbox

# In new terminal:
python3 test_phase2.py
```

### Expected Output

```
╔════════════════════════════════════════════════════════════╗
║           ChainPilot Phase 2 - Testing Suite             ║
╚════════════════════════════════════════════════════════════╝

============================================================
1. API Health Check
============================================================
✅ API is healthy: healthy
ℹ️  Web3 connected: True

============================================================
2. Wallet Creation
============================================================
✅ Wallet created: test_phase2
ℹ️  Address: 0x...

... (more tests) ...

============================================================
TEST SUMMARY
============================================================
✅ API Health
✅ Wallet Creation
✅ Balance Check
✅ TX Estimation
✅ Send Transaction
✅ TX Status
✅ Token Balance
✅ Audit History
✅ Network Info

============================================================
✅ ALL TESTS PASSED! (9/9)
✅ Phase 2 is working perfectly! 🎉
============================================================
```

---

## 🌐 Manual Testing (Interactive API Docs)

### Step 1: Start Server
```bash
python3 run.py --sandbox
```

### Step 2: Open Browser
Go to: **http://localhost:8000/docs**

### Step 3: Try Endpoints

#### Create a Wallet
1. Click `POST /api/v1/wallet/create`
2. Click "Try it out"
3. Enter: `{"wallet_name": "test_wallet"}`
4. Click "Execute"
5. ✅ You get a wallet address!

#### Check Balance
1. Click `GET /api/v1/wallet/balance`
2. Click "Try it out"
3. Click "Execute"
4. ✅ See 100 ETH balance!

#### Estimate Transaction
1. Click `POST /api/v1/transaction/estimate`
2. Enter:
```json
{
  "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
  "value": 0.1
}
```
3. Click "Execute"
4. ✅ See gas estimate and costs!

#### Send Transaction
1. Click `POST /api/v1/transaction/send`
2. Enter:
```json
{
  "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
  "value": 0.1
}
```
3. Click "Execute"
4. ✅ Get transaction hash!

#### Check Status
1. Copy the `tx_hash` from previous response
2. Click `GET /api/v1/transaction/{tx_hash}`
3. Paste the hash
4. Click "Execute"
5. ✅ See transaction confirmed!

---

## 🔥 Real Testnet Testing

Once sandbox tests pass, try with real testnet!

### Step 1: Get Testnet Funds

**Sepolia Faucets:**
- https://sepoliafaucet.com
- https://www.alchemy.com/faucets/ethereum-sepolia
- https://faucet.quicknode.com/ethereum/sepolia

**Steps:**
1. Create wallet (if not already)
2. Copy your wallet address
3. Visit faucet website
4. Paste address and request ETH
5. Wait 1-2 minutes

### Step 2: Start Server (Live Mode)

```bash
# Make sure .env has valid RPC URL
python3 run.py
```

No `--sandbox` flag = live mode!

### Step 3: Verify Balance

```bash
curl http://localhost:8000/api/v1/wallet/balance
```

Should show your testnet ETH.

### Step 4: Send Real Transaction

```bash
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
    "value": 0.001
  }'
```

### Step 5: Monitor on Explorer

Copy the `explorer_url` from response, open in browser to watch confirmation!

---

## 🧩 Testing Specific Features

### Test Gas Estimation

```bash
curl -X POST http://localhost:8000/api/v1/transaction/estimate \
  -H "Content-Type: application/json" \
  -d '{
    "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
    "value": 1.0
  }'
```

### Test Token Balance

```bash
# Sandbox mode - use test token
curl http://localhost:8000/api/v1/token/balance/0xtest_usdc

# Live mode - use real token (e.g., USDC on Sepolia)
curl http://localhost:8000/api/v1/token/balance/0x...
```

### Test Audit Logs

```bash
# Get all transactions
curl http://localhost:8000/api/v1/audit/transactions

# Get only confirmed
curl "http://localhost:8000/api/v1/audit/transactions?status=CONFIRMED"

# Get statistics
curl http://localhost:8000/api/v1/audit/statistics
```

---

## 📊 Verify Database

After running transactions, check the database:

```bash
# Install sqlite3 if needed
# brew install sqlite3  # macOS
# sudo apt install sqlite3  # Linux

# Query database
sqlite3 chainpilot.db

# SQL commands:
.tables                              # Show tables
SELECT * FROM transactions LIMIT 5;  # View transactions
SELECT * FROM events LIMIT 5;        # View events
.quit                                # Exit
```

---

## 🐛 Troubleshooting

### Server Won't Start

**Error:** `ModuleNotFoundError`
```bash
# Solution: Activate venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Error:** `.env file not found`
```bash
# Solution: Create config
cp .env.example .env
nano .env  # Add RPC URL
```

### Tests Fail

**Error:** `Connection refused`
```bash
# Solution: Start server first
python3 run.py --sandbox
```

**Error:** `No wallet loaded`
```bash
# Solution: Create wallet first
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "test_wallet"}'
```

### Live Mode Issues

**Error:** `Web3 not connected`
- Check RPC URL in `.env`
- Verify API key is valid
- Try different RPC provider

**Error:** `Insufficient funds`
- Get testnet ETH from faucet
- Wait for faucet transaction to confirm
- Check balance: `GET /api/v1/wallet/balance`

**Error:** `Transaction failed`
- Check you have enough ETH for gas
- Estimate first: `POST /transaction/estimate`
- Review error message in response

---

## ✅ Testing Checklist

### Phase 2 Complete Test

- [ ] Server starts in sandbox mode
- [ ] Can create wallet
- [ ] Can check balance (shows 100 ETH)
- [ ] Can estimate transaction
- [ ] Can send transaction (simulated)
- [ ] Can check transaction status
- [ ] Can view audit history
- [ ] Database contains transactions
- [ ] All automated tests pass
- [ ] Interactive API docs work

### Real Testnet Test

- [ ] Server starts in live mode
- [ ] Web3 connects to testnet
- [ ] Received testnet funds
- [ ] Balance shows correct amount
- [ ] Can estimate real transaction
- [ ] Can send real transaction
- [ ] Transaction appears on explorer
- [ ] Transaction confirms (~15 seconds)
- [ ] Database logs transaction
- [ ] Status updates to CONFIRMED

---

## 🎯 Best Practices

### Development
1. **Always test in sandbox first**
2. Use automated test script
3. Check database after each test
4. Review API docs for all endpoints

### Testnet Testing
1. **Use Sepolia** (most reliable faucets)
2. Start with small amounts (0.001 ETH)
3. Monitor explorer for confirmations
4. Keep track of gas costs

### Production Prep
1. Complete security audit
2. Test with multiple wallets
3. Stress test with many transactions
4. Monitor database performance
5. Set up error alerting

---

## 📚 Next Steps

### After Successful Testing

1. **Explore all endpoints** in API docs
2. **Review transaction logs** in database
3. **Read documentation**:
   - `PHASE2_SUMMARY.md` - Technical overview
   - `PHASE2_EXPLAINED.md` - How it works
4. **Try token operations** (in sandbox or with test tokens)
5. **Prepare for Phase 3** - Rule & Risk Engine

### Need Help?

- Check `PHASE2_EXPLAINED.md` for detailed explanations
- Review API docs at `/docs`
- Check database for transaction logs
- Review server logs for errors

---

## 🎉 You're Ready!

**Sandbox Mode:** Safe, fast, no setup needed
**Live Mode:** Real blockchain, real transactions
**Test Script:** Automated comprehensive testing
**API Docs:** Interactive testing interface

**Start testing:** `python3 run.py --sandbox`
**Then run:** `python3 test_phase2.py`

Happy testing! 🚀

