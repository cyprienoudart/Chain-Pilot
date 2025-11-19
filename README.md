# ChainPilot 🚀

**A secure bridge between AI agents and cryptocurrency networks**

ChainPilot is a REST API that allows AI agents (like ChatGPT, Claude, etc.) to autonomously manage crypto wallets and execute blockchain transactions with human oversight. Built with security-first principles using Python, FastAPI, and Web3.

---

## 🎯 What It Does

**Current (Phase 1 - ✅ Complete):**
- Create and manage encrypted crypto wallets
- Check balances across multiple blockchain networks
- View transaction history
- Multi-network support (Ethereum, Polygon, Sepolia, Mumbai, etc.)
- RESTful API with auto-generated documentation

**Future (Phases 2-6):**
- Execute transactions and send crypto
- ERC-20 token support
- Spending rules and risk management
- AI agent natural language integration
- Web dashboard for monitoring
- Production-ready security audit

---

## ⚡ Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure (add your RPC URL from Infura or Alchemy)
cp .env.example .env
nano .env  # Edit and add your RPC URL

# 3. Run
python3 run.py
```

**Then visit:** http://localhost:8000/docs

**📖 Full instructions:** See `QUICKSTART.md`

---

## 🏗️ Architecture

```
┌─────────────┐
│  AI Agent   │  (Future: ChatGPT, Claude, custom bots)
└──────┬──────┘
       │ HTTP/JSON
       ▼
┌──────────────────────────────┐
│  ChainPilot API (FastAPI)    │
│                              │
│  ┌────────────────────────┐  │
│  │  API Routes            │  │  ← Phase 1 ✅
│  │  - Wallet management   │  │
│  │  - Balance queries     │  │
│  └───────────┬────────────┘  │
│              │               │
│  ┌───────────┴────────────┐  │
│  │  Wallet Manager        │  │
│  │  (Encrypted storage)   │  │
│  └───────────┬────────────┘  │
│              │               │
│  ┌───────────┴────────────┐  │
│  │  Web3 Manager          │  │
│  │  (Blockchain RPC)      │  │
│  └───────────┬────────────┘  │
└──────────────┼───────────── ─┘
               │
               ▼
   ┌─────────────────────┐
   │  Blockchain Network │
   │  (Ethereum, Polygon)│
   └─────────────────────┘
```

---

## 🔐 Security

- **Encrypted Storage**: Private keys encrypted with PBKDF2 (100k iterations) + Fernet (AES-128)
- **Never Exposed**: Keys never appear in logs, API responses, or memory dumps
- **Password Protected**: Master password required for decryption
- **Testnet First**: Designed for safe testing on Sepolia/Mumbai
- **Open Source**: Transparent and auditable code

⚠️ **Status**: Phase 1 is testnet-ready. NOT audited for mainnet/production use.

---

## 📡 API Endpoints

### Current (Phase 1)
```
POST /api/v1/wallet/create    → Create encrypted wallet
POST /api/v1/wallet/load      → Load existing wallet
GET  /api/v1/wallet/list      → List all wallets
GET  /api/v1/wallet/current   → Get active wallet
GET  /api/v1/wallet/balance   → Check balance
GET  /api/v1/wallet/history   → Transaction history
GET  /api/v1/network/info     → Blockchain info
GET  /health                  → API health check
```

---

## 💻 Tech Stack

| Technology | Purpose | Why? |
|------------|---------|------|
| **Python 3.9+** | Language | Popular, AI-friendly ecosystem |
| **FastAPI** | Web framework | Fast, modern, auto-docs |
| **Web3.py** | Blockchain | Industry standard for Ethereum |
| **Cryptography** | Encryption | Bank-level key security |
| **Pydantic** | Validation | Type safety, auto-validation |
| **Uvicorn** | Server | High-performance ASGI |

---

## 📖 Example Usage

### Python Client
```python
import requests

# Create wallet
response = requests.post(
    "http://localhost:8000/api/v1/wallet/create",
    json={"wallet_name": "my_wallet"}
)
wallet = response.json()
print(f"Address: {wallet['address']}")

# Check balance
response = requests.get("http://localhost:8000/api/v1/wallet/balance")
balance = response.json()
print(f"Balance: {balance['balance_ether']} ETH")
```

### curl
```bash
# Create wallet
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "my_wallet"}'

# Check balance
curl http://localhost:8000/api/v1/wallet/balance
```

---

## 📂 Project Structure

```
Chain-Pilot/
├── src/
│   ├── api/
│   │   ├── main.py              # FastAPI application
│   │   └── routes.py            # API endpoints
│   └── execution/
│       ├── secure_execution.py  # Wallet manager (encrypted)
│       └── web3_connection.py   # Blockchain connection
│
├── tests/
│   ├── test_api.py              # API tests
│   └── test_imports.py          # Import verification
│
├── .env                         # Configuration (create from .env.example)
├── run.py                       # Startup script
├── requirements.txt             # Dependencies
│
├── README.md                    # This file
├── QUICKSTART.md                # Quick start guide
├── HOW_IT_WORKS.md              # Technical deep dive
└── ROADMAP.md                   # Development roadmap
```

---

## 🛠️ Development Roadmap

| Phase | Status | Features |
|-------|--------|----------|
| **Phase 1** | ✅ **Done** | Backend core, wallet management, balance checking |
| **Phase 2** | 📋 Next | Transaction execution, gas estimation, ERC-20 support |
| **Phase 3** | 🔜 Planned | Spending rules, risk engine, whitelists |
| **Phase 4** | 🔜 Planned | AI integration, natural language processing |
| **Phase 5** | 🔜 Planned | Web dashboard, real-time monitoring |
| **Phase 6** | 🔜 Planned | Security audit, production deployment |

**See `ROADMAP.md` for detailed breakdown**

---

## 🧪 Testing

```bash
# Test imports
python3 tests/test_imports.py

# Run test suite
pytest tests/ -v

# With coverage
pytest tests/ --cov=src
```

---

## 💡 Use Cases

### Current
- Personal wallet management
- Portfolio balance tracking
- Bot/automation balance monitoring
- Learning blockchain development

### Future
- AI agents making autonomous payments
- Automated DeFi operations
- Subscription payment automation
- Gaming economies
- Crypto payment processing for apps

---

## 📚 Documentation

- **`README.md`** (this file) - Project overview and basics
- **`QUICKSTART.md`** - Get running in 5 minutes
- **`HOW_IT_WORKS.md`** - Technical details, architecture, security
- **`ROADMAP.md`** - Development plan and next steps

**Interactive API Docs:** http://localhost:8000/docs (when running)

---

## 🤝 Contributing

Phase 1 is complete and working. Future phases welcome contributions:
- Transaction building (Phase 2)
- Rule engine (Phase 3)
- AI integration (Phase 4)
- Dashboard (Phase 5)

---

## 📄 License

MIT License - Free to use, modify, and commercialize.

---

## 🎯 Getting Help

1. **Quick start issues?** → See `QUICKSTART.md`
2. **Technical questions?** → See `HOW_IT_WORKS.md`
3. **Development questions?** → See `ROADMAP.md`
4. **Test the API?** → Visit http://localhost:8000/docs

---

**Built with ❤️ for the future of AI × Crypto**

Status: Phase 1 Complete ✅ | Next: Phase 2 Transaction Execution
