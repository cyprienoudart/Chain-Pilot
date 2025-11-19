# ChainPilot - Phase 1 Setup Guide

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.9+ installed
- Access to an Ethereum RPC provider (Infura, Alchemy, or similar)
- Git (optional, for version control)

### 2. Installation

```bash
# Clone or navigate to the project directory
cd Chain-Pilot

# Create virtual environment (if not already created)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy the environment template
cp env_template.txt .env

# Edit .env file with your configuration
# REQUIRED: Set WEB3_RPC_URL with your RPC endpoint
# REQUIRED: Set WALLET_PASSWORD to a secure password
```

**Getting an RPC URL:**

**Infura** (Recommended for beginners):
1. Sign up at https://infura.io
2. Create a new project
3. Copy the Sepolia endpoint URL
4. Add to .env: `WEB3_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID`

**Alchemy**:
1. Sign up at https://alchemy.com
2. Create a new app (Ethereum Sepolia)
3. Copy the HTTPS URL
4. Add to .env: `WEB3_RPC_URL=https://eth-sepolia.g.alchemy.com/v2/YOUR_API_KEY`

### 4. Run the API

```bash
# Make sure you're in the project root directory
python -m src.api.main

# Or use uvicorn directly:
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: http://localhost:8000

### 5. Test the API

**Interactive API Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Quick Test:**
```bash
# Check API status
curl http://localhost:8000/

# Check health
curl http://localhost:8000/health

# Create a wallet
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "my_first_wallet"}'

# Get balance
curl http://localhost:8000/api/v1/wallet/balance
```

## 📋 Available Endpoints

### Core Endpoints
- `GET /` - API status
- `GET /health` - Health check

### Wallet Management
- `POST /api/v1/wallet/create` - Create new wallet
- `POST /api/v1/wallet/load` - Load existing wallet
- `GET /api/v1/wallet/list` - List all wallets
- `GET /api/v1/wallet/current` - Get current wallet

### Balance & History
- `GET /api/v1/wallet/balance` - Get wallet balance
- `GET /api/v1/wallet/history` - Get transaction history

### Network Info
- `GET /api/v1/network/info` - Get blockchain network info

## 🔒 Security Notes

**Phase 1 Security:**
- Private keys are encrypted using PBKDF2 + Fernet
- Keys are stored locally in encrypted JSON files
- Master password is required (set in .env)

**⚠️ Important:**
- This is a development/MVP setup
- NOT production-ready for mainnet/real funds
- Use only on testnets (Sepolia, Mumbai, etc.)
- For production, consider: HSM, MPC wallets, or hardware wallets

## 🧪 Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest --cov=src tests/
```

## 🐛 Troubleshooting

**"Web3 not connected" error:**
- Check your RPC URL in .env
- Verify your API key is valid
- Test the RPC endpoint directly

**"No wallet loaded" error:**
- Create a wallet first: `POST /api/v1/wallet/create`
- Or load an existing wallet: `POST /api/v1/wallet/load`

**"Module not found" errors:**
- Make sure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Port already in use:**
- Change port in command: `--port 8001`
- Or kill the process using port 8000

## 📁 Project Structure

```
Chain-Pilot/
├── src/
│   ├── api/
│   │   ├── main.py          # FastAPI application
│   │   └── routes.py        # API endpoints
│   ├── execution/
│   │   ├── web3_connection.py   # Web3 manager
│   │   └── secure_execution.py  # Wallet manager
│   └── ...
├── tests/
│   └── test_api.py          # API tests
├── wallets/                 # Encrypted wallet storage
├── .env                     # Your configuration (create from template)
├── env_template.txt         # Environment template
├── requirements.txt         # Python dependencies
└── README.md
```

## 🎯 Next Steps

Once Phase 1 is running:
1. Test wallet creation and balance checking
2. Get testnet ETH from faucet (https://sepoliafaucet.com)
3. Move to Phase 2: Transaction execution
4. Implement Phase 3: Rule & Risk Engine
5. Build Phase 4: AI integration
6. Create Phase 5: Dashboard

## 💡 Getting Testnet ETH

**Sepolia Faucets:**
- https://sepoliafaucet.com
- https://www.alchemy.com/faucets/ethereum-sepolia
- https://faucet.quicknode.com/ethereum/sepolia

**Polygon Mumbai Faucets:**
- https://faucet.polygon.technology/
- https://mumbaifaucet.com/

## 📚 Resources

- FastAPI Documentation: https://fastapi.tiangolo.com
- Web3.py Documentation: https://web3py.readthedocs.io
- Ethereum Documentation: https://ethereum.org/developers
- Infura: https://docs.infura.io
- Alchemy: https://docs.alchemy.com

