# ChainPilot – Detailed Architecture & Implementation Guide

This document explains in detail how ChainPilot will be built, the technologies involved, and the step-by-step plan to develop the full platform.

---

# 🏛️ 1. High-Level Architecture

ChainPilot is structured into 4 independent but interconnected modules:
``` 
AI Agent
↓
AI Proxy API (Python)
↓
Rule & Risk Engine (Python)
↓
Secure Execution Layer (Web3 + MPC wallets)
↓
Blockchain Network (Ethereum, Polygon, etc.)
```
Each layer has a clear responsibility, strong isolation, and strict security boundaries.

---

# 🧠 2. AI Proxy API (Python)

### **Purpose**
This is the *only* component the AI interacts with.  
It acts as a translator between natural-language AI requests and actionable financial instructions.

### **Responsibilities**
- Receive requests from the AI (JSON format)
- Validate schemas (FastAPI automatic validation)
- Convert NL intent → structured actions
- Reject malformed or suspicious inputs early

### **Technologies**
- **FastAPI** (recommended for async + speed)
- **pydantic** (request validation)
- **uvicorn** (server)

### **Endpoints**
- `POST /transaction/simulate`
- `POST /transaction/execute`
- `GET /wallet/balance`
- `GET /wallet/history`
- `GET /rules`

---

# ⚖️ 3. Rule & Risk Engine

### **Purpose**
Ensure the AI never spends money outside allowed boundaries.

### **Checks performed**
- Daily/weekly spending limits  
- Max per-transaction amount  
- Allowed wallet addresses  
- Allowed tokens  
- Behavior anomaly detection  

### **Output**
The engine returns:

| Decision | Meaning |
|---------|----------|
| **ALLOW** | Execute immediately |
| **REQUIRE_CONFIRMATION** | Wait for human validation |
| **DENY** | Block and log |

### **Technologies**
- Python module integrated inside the API
- Optional future ML anomaly detection

---

# 🔐 4. Secure Execution Layer

### **Purpose**
Execute crypto payments **safely** without ever exposing private keys.

### **Security Techniques**
- Non-exportable encrypted key storage
- MPC wallet (Fireblocks-style architecture, open-source alternatives possible)
- Optional hardware integration later (Ledger, Trezor)

### **Responsibilities**
- Build and sign transactions
- Broadcast through reliable RPC provider
- Maintain a tamper-proof audit log

### **Technologies**
- **web3.py**
- Encrypted keys using **cryptography** library
- RPC nodes (Infura, Alchemy, or self-hosted)

---

# 🖥️ 5. Dashboard & Monitoring

### **Purpose**
Allow the user to:
- Monitor AI behavior
- See all pending or past transactions
- Configure rules
- Approve or reject confirmation-required actions

### **Style**
- Minimalist
- Black & white
- Graphs, clean spacing, strong typography

### **Tech Stack**
- **Frontend**: HTML + minimal JS or a lightweight React app
- **Backend**: Same API, separate routes for dashboard
- **Graphs**: chart.js or ECharts

### **Dashboard Elements**
- Latest AI requests list
- Spending over time graph
- Allowed vs blocked transactions
- Risk alerts
- User-defined security rules

---

# 📦 6. Step-by-Step Development Plan

### **Phase 1 – Foundations (Backend core)** ✅ **COMPLETED**
**Status**: Implemented and ready for testing

**What's Built:**
1. ✅ FastAPI backend with async lifecycle management
2. ✅ Web3 connection manager supporting multiple networks (Sepolia, Mumbai, Ethereum, Polygon)
3. ✅ Secure wallet creation and management with encrypted private key storage
4. ✅ Balance and transaction history endpoints
5. ✅ Health check and network info endpoints
6. ✅ Comprehensive test suite
7. ✅ Environment configuration and setup documentation

**Technical Details:**
- **Web3 Manager** (`src/execution/web3_connection.py`):
  - Multi-network support with configurable RPC endpoints
  - Connection health monitoring
  - Gas price and block number tracking
  - Support for both HTTP and WebSocket providers
  - PoA middleware for Polygon networks

- **Wallet Manager** (`src/execution/secure_execution.py`):
  - PBKDF2 + Fernet encryption for private keys
  - Secure key derivation with 100,000 iterations
  - Encrypted JSON wallet storage
  - Support for multiple wallets
  - Balance and transaction count queries

- **API Layer** (`src/api/main.py`, `src/api/routes.py`):
  - RESTful API with automatic validation (Pydantic)
  - CORS support for future dashboard integration
  - Comprehensive error handling and logging
  - Interactive API documentation (Swagger/ReDoc)

**Endpoints Implemented:**
- `GET /` - API status
- `GET /health` - Health check with Web3 connection status
- `POST /api/v1/wallet/create` - Create encrypted wallet
- `POST /api/v1/wallet/load` - Load existing wallet
- `GET /api/v1/wallet/list` - List available wallets
- `GET /api/v1/wallet/current` - Get current wallet address
- `GET /api/v1/wallet/balance` - Get native token balance
- `GET /api/v1/wallet/history` - Get transaction history
- `GET /api/v1/network/info` - Get blockchain network info

**Security Implemented:**
- Encrypted private key storage using industry-standard cryptography
- Environment-based configuration (no hardcoded secrets)
- Password-based key derivation (PBKDF2)
- Secure key never exposed in API responses
- Audit-ready logging

**Testing:**
- Unit tests for all API endpoints
- Mocked Web3 and wallet managers for isolated testing
- Test coverage for happy paths and error cases

**How to Use:**
See `SETUP.md` for detailed setup instructions and API usage examples.

---

### **Phase 2 – Execution Layer** 🔄 **NEXT**
5. Add transaction builder with gas estimation
6. Implement transaction signing and broadcasting
7. Add ERC-20 token support
8. Create audit log system (database integration)
9. Add transaction simulation
10. Implement retry logic and error handling

### **Phase 3 – Rule & Risk Engine**
11. Design rule schema and storage
12. Implement spending limit rules (daily/weekly/per-transaction)
13. Add whitelist/blacklist for addresses and tokens
14. Create rule evaluation engine (ALLOW/DENY/CONFIRM)
15. Add behavioral anomaly detection
16. Build rule management API endpoints

### **Phase 4 – AI Proxy**
17. Define standardized JSON request/response format for AI agents
18. Create transaction simulation endpoint for AI
19. Implement AI-friendly execute endpoint with natural language support
20. Add intent parsing and validation
21. Create AI-specific error messages and guidance
22. Build example integration for ChatGPT/Claude

### **Phase 5 – Dashboard**
23. Design minimalist black & white UI
24. Build real-time transaction monitoring
25. Add spending graphs (daily/weekly/monthly)
26. Create rule editor interface
27. Implement approval workflow for flagged transactions
28. Add wallet management UI

### **Phase 6 – MVP Finalization**
29. End-to-end integration testing
30. Security audit and penetration testing
31. Performance optimization
32. Complete API and integration documentation
33. Create video tutorials and examples
34. Launch open-source MVP on GitHub  

---

# 🧱 7. Tech Stack Summary

| Component | Technology |
|----------|------------|
| Backend Server | Python (FastAPI) |
| Web3 Layer | web3.py |
| Security | cryptography, encrypted key vault, MPC (optional) |
| Dashboard Frontend | JS/HTML or small React |
| Database (logs & rules) | SQLite or PostgreSQL |
| AI Interface | JSON API compatible with any LLM |

---

# 🔮 8. Future Extensions

- Multi-agent shared wallets  
- Subscription automation  
- On-chain spending rules (smart contract wallets)  
- AI anomaly detection model  
- Cross-chain support (Solana, Avalanche, etc.)  

---

# ✔️ Conclusion

ChainPilot’s architecture is built to be:

- **Secure**
- **Modular**
- **LLM-friendly**
- **Scalable**
- **Realistic for an MVP**

It provides the first safe bridge allowing AI to interact with real crypto assets.