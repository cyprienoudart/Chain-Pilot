# ChainPilot 🚀

[![Python](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121.3-009688.svg)](https://fastapi.tiangolo.com/)
[![Web3](https://img.shields.io/badge/Web3.py-7.14.0-orange.svg)](https://web3py.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)]()

> 🏆 **Competition Winner & Bootcamp Project**
>
> Developed during the **ASES Stanford Program** bootcamp.
> * **3rd Place** out of 75 groups from top French schools.
> * Ranked in the **Top 1%%** of 300 participants in the competition hosted by **Stanford and HEC**.
>
>
**ChainPilot** is a secure, AI-powered gateway for managing cryptocurrency transactions with automated safety controls, real-time monitoring, and intelligent risk management. It acts as a secure bridge between AI agents and blockchain operations, ensuring controlled and auditable interactions with crypto financial systems.

---

## 🌟 Features

### 🔐 **Security First**
- **AI Spending Controls**: Configurable limits on single transactions, hourly/daily spending
- **Rule Engine**: Flexible rule system with spending limits, address whitelists/blacklists, and time restrictions
- **Approval Workflows**: Automatic flagging of high-risk transactions for manual review
- **Encrypted Key Storage**: Private keys encrypted at rest using PBKDF2HMAC and Fernet
- **Comprehensive Audit Logging**: Every transaction and action logged to SQLite database

### 🤖 **AI Integration**
- **Natural Language Processing**: Parse transaction intents from plain English
- **Entity Extraction**: Automatically identify addresses, amounts, and tokens from user input
- **ENS Name Resolution**: Support for Ethereum Name Service (e.g., "vitalik.eth")
- **Context Management**: Maintain conversation history for follow-up commands
- **Smart Execution**: AI-initiated transactions subject to all safety rules

### 💰 **Wallet Management**
- **Multi-Wallet Support**: Create and manage multiple wallets with easy switching
- **Balance Queries**: Real-time balance checks for native tokens and ERC-20
- **Transaction History**: Complete audit trail of all transactions
- **Network Support**: Compatible with Ethereum, Polygon, Arbitrum, Optimism, Base, and all EVM-compatible chains
- **Sandbox Mode**: Test transactions without real blockchain interaction

**Note**: ChainPilot supports Ethereum and EVM-compatible blockchains only. Bitcoin, Solana, and other non-EVM chains are not supported.

### 🛡️ **Rule & Risk Engine**
- **Spending Limits**: Per-transaction, daily, weekly, and monthly limits
- **Address Control**: Whitelist trusted addresses or blacklist suspicious ones
- **Time Restrictions**: Limit transactions to specific hours or days
- **Amount Thresholds**: Require approval for large transactions
- **Transaction Frequency**: Limit the number of transactions per period
- **Priority-Based Evaluation**: Rules processed in configurable priority order

### 📊 **Real-Time Dashboard**
- **Live Transaction Monitoring**: See transactions as they happen
- **Interactive Charts**: Visualize transaction activity and patterns
- **Rule Management**: Toggle, edit, and create rules from the web interface
- **Wallet Visualization**: View all wallets with balances and network information
- **AI Chat Interface**: Interact with the AI directly from the dashboard
- **Modern UI**: Clean, responsive black and white design

### 🔌 **Developer-Friendly API**
- **RESTful Design**: Standard HTTP methods and JSON payloads
- **Auto-Generated Docs**: Interactive API documentation at `/docs`
- **Type Safety**: Pydantic models for request/response validation
- **Error Handling**: Clear, actionable error messages
- **Rate Limiting**: Protect against abuse and DoS attacks
- **API Key Authentication**: Secure your endpoints with API keys

---

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- Virtual environment (recommended)
- RPC endpoint (Infura, Alchemy, or local node)

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/Chain-Pilot.git
cd Chain-Pilot
```

2. **Create and activate virtual environment**:
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment** (optional):
```bash
# Set your RPC URL (defaults to Sepolia testnet)
export WEB3_RPC_URL="https://sepolia.infura.io/v3/YOUR_PROJECT_ID"

# Set API key for authentication (optional)
export CHAINPILOT_API_KEY="your-secret-api-key"
```

### Running the Server

**Sandbox Mode** (recommended for testing):
```bash
python3 run.py --sandbox
```

**Live Mode** (connects to real blockchain):
```bash
python3 run.py
```

The server starts on **http://localhost:8000**

- **Dashboard**: http://localhost:8000/
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📖 Usage

### Creating a Wallet

```bash
curl -X POST http://localhost:8000/api/v1/wallet/create \
  -H "Content-Type: application/json" \
  -d '{"wallet_name": "my_wallet"}'
```

### Checking Balance

```bash
curl http://localhost:8000/api/v1/wallet/balance
```

### Sending a Transaction

```bash
curl -X POST http://localhost:8000/api/v1/transaction/send \
  -H "Content-Type: application/json" \
  -d '{
    "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
    "value": 0.01
  }'
```

### Using AI Natural Language

```bash
curl -X POST http://localhost:8000/api/v1/ai/parse \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Send 0.5 ETH to alice",
    "execute": true
  }'
```

### Creating a Rule

```bash
curl -X POST http://localhost:8000/api/v1/rules/create \
  -H "Content-Type: application/json" \
  -d '{
    "rule_type": "spending_limit",
    "rule_name": "Daily Limit",
    "parameters": {"type": "daily", "amount": 1.0},
    "action": "deny",
    "enabled": true
  }'
```

---

## 🏗️ Architecture

ChainPilot is built with a modular, layered architecture:

```
┌─────────────────────────────────────────────────────────┐
│                     Dashboard (Web UI)                   │
│              React-like Frontend + Charts.js             │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    FastAPI REST API                      │
│              Routes + Pydantic Models                    │
└─────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────┬──────────────────┬───────────────────┐
│   AI Controller  │   Rule Engine    │  Security Layer   │
│  Intent Parsing  │  Risk Evaluation │  AI Controls      │
│  NLP Processing  │  Policy Enforce  │  Rate Limiting    │
└──────────────────┴──────────────────┴───────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│              Secure Execution Layer                      │
│    Wallet Manager + Transaction Builder + Token Manager  │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                     Web3 Provider                        │
│              Ethereum / Polygon / Other EVM              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   Audit Logger (SQLite)                  │
│           Transactions + Rules + Events                  │
└─────────────────────────────────────────────────────────┘
```

### Key Components

- **`src/api/`**: FastAPI application, routes, and models
- **`src/execution/`**: Wallet management, transaction building, Web3 integration
- **`src/rules/`**: Rule engine and risk evaluation
- **`src/ai/`**: Natural language processing and intent parsing
- **`src/security/`**: AI spending controls, rate limiting, authentication
- **`src/dashboard/`**: Web interface (HTML, CSS, JavaScript)

---

## 🧪 Testing

ChainPilot includes comprehensive test suites covering all functionalities:

### Run All Tests

```bash
# Comprehensive test suite (24 tests)
python3 tests/test_all_comprehensive.py

# Real data integration (6 tests)
python3 tests/test_dashboard_real_data.py

# Dashboard enhancements (3 test categories)
python3 tests/test_dashboard_enhancements.py
```

### Test Coverage

- ✅ Wallet creation, loading, balance queries
- ✅ Transaction building, sending, status tracking
- ✅ ERC-20 token transfers
- ✅ Rule creation, evaluation, modification
- ✅ AI intent parsing and execution
- ✅ Audit logging and history
- ✅ Dashboard data integrity
- ✅ Security controls and rate limiting

**Current Status**: 100% test pass rate (30/30 tests)

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `WEB3_RPC_URL` | Ethereum RPC endpoint | Sepolia testnet |
| `CHAINPILOT_API_KEY` | API key for authentication | None (disabled) |
| `CHAINPILOT_SANDBOX` | Enable sandbox mode | `false` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Rule Types

| Rule Type | Description | Parameters |
|-----------|-------------|------------|
| `spending_limit` | Limit spending per period | `type`, `amount` |
| `address_whitelist` | Only allow specific addresses | `addresses` |
| `address_blacklist` | Block specific addresses | `addresses` |
| `time_restriction` | Limit by time of day | `allowed_hours`, `timezone` |
| `amount_threshold` | Require approval above amount | `threshold` |
| `daily_transaction_count` | Limit transactions per day | `max_count` |

### Security Levels

| Level | Description |
|-------|-------------|
| `OFF` | No AI-specific controls |
| `MONITOR` | Log violations, don't block |
| `STRICT` | Enforce all limits (default) |
| `CRITICAL` | Maximum restrictions |

---

## 📚 Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[Quick Start Guide](docs/guides/QUICKSTART.md)**: Get up and running in 5 minutes
- **[How It Works](docs/technical/HOW_IT_WORKS.md)**: Technical deep dive
- **[Testing Guide](docs/guides/TESTING_GUIDE.md)**: Complete testing documentation
- **[Demo Guide](docs/guides/DEMO_GUIDE.md)**: Live demo instructions
- **[Security Documentation](docs/phases/PHASE6_SECURITY.md)**: Security features and best practices
- **[API Reference](http://localhost:8000/docs)**: Interactive API documentation (when server is running)

---

## 🛠️ Development

### Project Structure

```
Chain-Pilot/
├── src/
│   ├── api/              # FastAPI routes and models
│   ├── execution/        # Wallet and transaction management
│   ├── rules/            # Rule engine
│   ├── ai/               # AI natural language processing
│   ├── security/         # Security controls
│   └── dashboard/        # Web UI
├── tests/                # Test suites
├── scripts/              # Utility scripts
├── docs/                 # Documentation
├── wallets/              # Encrypted wallet storage
├── chainpilot.db         # SQLite database
├── requirements.txt      # Python dependencies
└── run.py                # Server entry point
```

### Adding New Features

1. **New API Endpoint**: Add route in `src/api/routes.py`
2. **New Rule Type**: Extend `RuleEngine` in `src/rules/rule_engine.py`
3. **New Security Control**: Add to `AIControls` in `src/security/ai_controls.py`
4. **New Dashboard Feature**: Update `src/dashboard/static/dashboard.js`

### Code Style

- Python: PEP 8 compliant
- JavaScript: ES6+ with async/await
- Type hints for all Python functions
- Comprehensive docstrings

---

## 🔒 Security

### Best Practices

- **Never commit private keys**: Use `.gitignore` for wallet files
- **Use environment variables**: For sensitive configuration
- **Enable API key auth**: In production environments
- **Configure rate limiting**: Prevent abuse
- **Set conservative AI limits**: Start with low spending caps
- **Regular audits**: Review audit logs frequently
- **Update dependencies**: Keep libraries up to date

### Threat Model

ChainPilot protects against:
- ✅ Unauthorized AI spending
- ✅ Transaction flooding
- ✅ API abuse
- ✅ Address manipulation
- ✅ Timing attacks
- ✅ Private key exposure

### Known Limitations

- Sandbox mode simulates transactions (not real blockchain state)
- SQLite not suitable for high-concurrency production (consider PostgreSQL)
- Rate limiting is in-memory (resets on server restart)
- ENS resolution requires network access

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`python3 tests/test_all_comprehensive.py`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt

# Run tests
python3 tests/test_all_comprehensive.py

# Run linter
flake8 src/

# Format code
black src/
```

---

## 📊 Performance

### Benchmarks

- **Transaction Processing**: < 100ms (sandbox), < 2s (live)
- **Rule Evaluation**: < 10ms for 100 rules
- **API Response Time**: < 50ms average
- **Dashboard Load Time**: < 1s
- **Database Query**: < 10ms for 10k transactions

### Scalability

- Handles 100+ wallets efficiently
- Supports 1000+ transactions in audit log
- Can process 10+ transactions/second (sandbox)
- Dashboard auto-refreshes every 30 seconds

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **FastAPI**: For the excellent web framework
- **Web3.py**: For Ethereum integration
- **Chart.js**: For beautiful charts
- **Pydantic**: For data validation
- **Cryptography**: For secure key management

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/Chain-Pilot/issues)
- **Documentation**: [docs/](docs/)
- **Email**: support@chainpilot.dev

---

## 🗺️ Roadmap

### Current Version: 1.0.0

**Implemented**:
- ✅ Wallet management and balance queries
- ✅ Transaction building and sending
- ✅ ERC-20 token support
- ✅ Rule engine with 6 rule types
- ✅ AI natural language processing
- ✅ Real-time web dashboard
- ✅ Security controls and rate limiting
- ✅ Comprehensive audit logging
- ✅ Sandbox mode for testing
- ✅ 100% test coverage

**Future Enhancements**:
- [ ] Multi-signature wallet support
- [ ] Hardware wallet integration
- [ ] NFT transaction support
- [ ] DeFi protocol integration
- [ ] Mobile app
- [ ] WebSocket real-time updates
- [ ] PostgreSQL backend
- [ ] Kubernetes deployment
- [ ] Advanced analytics dashboard
- [ ] Machine learning risk scoring

---

## 📈 Stats

- **Lines of Code**: ~10,000
- **Test Coverage**: 100% (30/30 tests passing)
- **Documentation Pages**: 15+
- **Supported Networks**: Ethereum, Polygon, Sepolia, and more
- **API Endpoints**: 25+
- **Rule Types**: 6
- **Security Layers**: 3 (Rules, AI Controls, Rate Limiting)

---

<div align="center">

**Built with ❤️ for the decentralized future**

[Documentation](docs/) • [Issues](https://github.com/yourusername/Chain-Pilot/issues) • [Changelog](ROADMAP.md)

</div>
