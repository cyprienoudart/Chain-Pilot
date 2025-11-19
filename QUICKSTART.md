# ⚡ Quick Start Guide

Get ChainPilot running in 5 minutes.

---

## 🚀 Three Commands

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
nano .env  # Add your RPC URL (see below)

# 3. Run
python3 run.py
```

**Then open:** http://localhost:8000/docs

---

## 🔑 Get Your RPC URL (Required!)

You need a free RPC endpoint to connect to the blockchain.

### Option 1: Infura (Easiest)
1. Go to https://infura.io
2. Sign up (free)
3. Create new project → Web3 API
4. Copy **Sepolia** endpoint URL
5. Paste into `.env` as `WEB3_RPC_URL`

**Example URL:**
```
https://sepolia.infura.io/v3/abc123def456...
```

### Option 2: Alchemy
1. Go to https://alchemy.com
2. Sign up (free)
3. Create app → Ethereum → Sepolia
4. Copy **HTTPS** URL
5. Paste into `.env` as `WEB3_RPC_URL`

**Example URL:**
```
https://eth-sepolia.g.alchemy.com/v2/abc123...
```

---

## 📝 Configuration File

Your `.env` file should look like this:

```bash
# Blockchain Network
WEB3_NETWORK=sepolia

# RPC URL (from Infura or Alchemy)
WEB3_RPC_URL=https://sepolia.infura.io/v3/YOUR_API_KEY_HERE

# Wallet encryption password (change this!)
WALLET_PASSWORD=my_super_secure_password_12345

# Wallet storage (optional, defaults to ./wallets)
WALLET_DIR=./wallets
```

**⚠️ Important:**
- Change `WALLET_PASSWORD` to something secure
- Never commit `.env` to git (it's in `.gitignore`)

---

## ✅ Verify It Works

Once running, you should see:

```
🚀 Starting ChainPilot API...
📚 Docs will be at: http://localhost:8000/docs

INFO: Started server process
INFO: Waiting for application startup.
INFO: Connected to Sepolia Testnet (Chain ID: 11155111)
INFO: ChainPilot API started successfully
INFO: Application startup complete.
INFO: Uvicorn running on http://0.0.0.0:8000
```

---

## 🧪 Test the API

### Method 1: Interactive Docs (Easiest)
1. Open http://localhost:8000/docs
2. Click **POST /api/v1/wallet/create**
3. Click "Try it out"
4. Click "Execute"
5. See your new wallet address!

### Method 2: curl
```bash
# Health check
curl http://localhost:8000/health

# Create wallet
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "my_wallet"}'

# Check balance
curl http://localhost:8000/api/v1/wallet/balance
```

### Method 3: Python
```python
import requests

# Create wallet
r = requests.post(
    "http://localhost:8000/api/v1/wallet/create",
    json={"wallet_name": "test"}
)
print(r.json())
```

---

## 🎯 What You Can Do Now

### Current Features (Phase 1)
- ✅ Create encrypted wallets
- ✅ Check balances
- ✅ View transaction history
- ✅ Switch networks
- ✅ List all wallets

### Get Testnet Funds
Your wallet starts with 0 ETH. Get free testnet tokens:

**Sepolia Faucets:**
- https://sepoliafaucet.com
- https://www.alchemy.com/faucets/ethereum-sepolia
- https://faucet.quicknode.com/ethereum/sepolia

**Polygon Mumbai Faucets:**
- https://faucet.polygon.technology/
- https://mumbaifaucet.com/

---

## 💡 Common Issues

### "No module named 'web3'"
```bash
# Activate virtual environment
source .venv/bin/activate  # or: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### ".env file not found"
```bash
# Create from template
cp .env.example .env

# Edit with your RPC URL
nano .env
```

### "Web3 not connected"
- Check your RPC URL in `.env`
- Verify your API key is valid
- Try a different RPC provider

### "Connection refused" when testing
- Make sure server is running: `python3 run.py`
- Check if port 8000 is already in use

---

## 📚 Next Steps

1. **Try the API** → Visit http://localhost:8000/docs
2. **Understand the code** → Read `HOW_IT_WORKS.md`
3. **See the roadmap** → Read `ROADMAP.md`
4. **Full details** → Read `README.md`

---

## 🧪 Advanced: Test Imports

Before running the server, verify all dependencies:

```bash
python3 tests/test_imports.py
```

Should output:
```
✅ All imports successful!
You're ready to run: python3 run.py
```

---

## 🎯 Quick Reference

| Action | Command |
|--------|---------|
| Start server | `python3 run.py` |
| Test imports | `python3 tests/test_imports.py` |
| Run tests | `pytest tests/ -v` |
| API docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

---

**That's it! You're ready to build.** 🚀

Need help? Check the full docs in `README.md` or technical details in `HOW_IT_WORKS.md`
