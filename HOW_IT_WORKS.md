# How ChainPilot Works - Technical Documentation

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Project Structure](#project-structure)
3. [Architecture & Data Flow](#architecture--data-flow)
4. [Core Components](#core-components)
5. [Security Implementation](#security-implementation)
6. [Technology Choices](#technology-choices)
7. [Request Lifecycle](#request-lifecycle)
8. [Future Architecture](#future-architecture)

---

## 🎯 System Overview

ChainPilot is a **secure REST API** that acts as a middleware layer between applications (especially AI agents) and blockchain networks. Think of it as a **crypto wallet backend** with enterprise-grade security and AI-friendly interfaces.

### What Problem Does It Solve?

**Problem**: AI agents can suggest crypto transactions but can't execute them safely.

**Solution**: ChainPilot provides:
- Secure wallet management with encrypted keys
- RESTful API for easy integration
- Transaction validation and rules (future)
- Human oversight capabilities
- Multi-network blockchain support

---

## 📂 Project Structure

```
Chain-Pilot/
│
├── 📝 Configuration & Docs
│   ├── .env.example             # Configuration template
│   ├── .env                     # Your config (gitignored)
│   ├── .gitignore               # Git exclusions
│   ├── requirements.txt         # Python dependencies
│   ├── run.py                   # Startup script
│   │
│   ├── README.md                # Project overview
│   ├── QUICKSTART.md            # Quick start guide
│   ├── HOW_IT_WORKS.md          # This file
│   └── ROADMAP.md               # Development roadmap
│
├── 💻 Source Code
│   └── src/
│       ├── __init__.py
│       │
│       ├── api/                 # API Layer
│       │   ├── __init__.py
│       │   ├── main.py          # FastAPI app & lifecycle
│       │   └── routes.py        # API endpoints
│       │
│       ├── execution/           # Execution Layer
│       │   ├── __init__.py
│       │   ├── secure_execution.py   # Wallet manager
│       │   └── web3_connection.py    # Web3 manager
│       │
│       ├── rules/               # Phase 3: Rule Engine
│       │   ├── __init__.py
│       │   └── rule_engine.py   # (placeholder)
│       │
│       └── dashboard/           # Phase 5: Dashboard
│           ├── __init__.py
│           └── dashboard_interface.py  # (placeholder)
│
├── 🧪 Tests
│   ├── __init__.py
│   ├── test_api.py              # API endpoint tests
│   └── test_imports.py          # Import verification
│
├── 🔒 Data (auto-created, gitignored)
│   └── wallets/                 # Encrypted wallet storage
│       ├── wallet1.json
│       └── wallet2.json
│
└── 📄 Other
    ├── LICENSE                  # MIT License
    └── Config/                  # Backup configs
```

### File Responsibilities

#### `src/api/main.py` - Application Core
- FastAPI application initialization
- Async lifecycle management (startup/shutdown)
- Global state management (Web3, Wallet managers)
- CORS middleware configuration
- Logging setup

#### `src/api/routes.py` - API Endpoints
- All HTTP endpoints definition
- Request/response models (Pydantic)
- Input validation
- Error handling
- Business logic coordination

#### `src/execution/web3_connection.py` - Blockchain Interface
- Web3 connection management
- Multi-network support
- RPC provider handling
- Balance queries
- Transaction lookups
- Network information retrieval

#### `src/execution/secure_execution.py` - Wallet Security
- Wallet creation (keypair generation)
- Private key encryption/decryption
- Encrypted file storage
- Wallet loading
- Balance checking
- Transaction history queries

#### `tests/test_api.py` - Test Suite
- Unit tests for all endpoints
- Mocked dependencies
- Integration test scenarios

#### `run.py` - Startup Script
- Environment validation
- Server initialization
- Configuration checks

---

## 🏗️ Architecture & Data Flow

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      EXTERNAL WORLD                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  [AI Agents]  [Web Apps]  [CLI Tools]  [Other Services]    │
│                                                              │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTP/HTTPS (JSON)
                         │
                         ▼
┌──────────────────────────────────────────────────────────────┐
│                     API LAYER (FastAPI)                      │
│                      src/api/                                │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  main.py                     routes.py                       │
│  ┌─────────────────┐        ┌──────────────────────┐       │
│  │ App Lifecycle   │        │ Endpoints            │       │
│  │ - Startup       │        │ - /wallet/create     │       │
│  │ - Shutdown      │        │ - /wallet/balance    │       │
│  │ - State Mgmt    │        │ - /wallet/history    │       │
│  │ - CORS          │        │ - /network/info      │       │
│  │ - Logging       │        │ - /health            │       │
│  └─────────────────┘        └──────────────────────┘       │
│                                                              │
│  📚 Auto-generated docs at /docs and /redoc                 │
└────────────┬──────────────────────────┬──────────────────────┘
             │                          │
    ┌────────┴────────┐        ┌────────┴────────┐
    ▼                 ▼        ▼                 ▼
┌─────────────┐   ┌─────────────────────────────────┐
│   WALLET    │   │     WEB3 MANAGER                │
│   MANAGER   │   │  src/execution/web3_connection  │
├─────────────┤   ├─────────────────────────────────┤
│ secure_     │   │                                 │
│ execution.py│   │  🌐 Multi-Network Support:      │
│             │   │  ├─ Ethereum (Mainnet)          │
│ 🔐 Security │   │  ├─ Ethereum Sepolia (Testnet)  │
│ ├─ Create   │   │  ├─ Polygon (Mainnet)           │
│ ├─ Encrypt  │   │  ├─ Polygon Mumbai (Testnet)    │
│ ├─ Load     │   │  └─ Any EVM-compatible chain    │
│ ├─ Balance  │   │                                 │
│ └─ History  │   │  📡 RPC Connection:             │
│             │   │  ├─ HTTP/WebSocket providers    │
│             │   │  ├─ Connection pooling          │
│             │   │  └─ Health monitoring           │
└──────┬──────┘   └────────┬────────────────────────┘
       │                   │
       │                   │
       ▼                   ▼
┌──────────────┐    ┌───────────────────────────────┐
│  LOCAL       │    │  BLOCKCHAIN NETWORK           │
│  STORAGE     │    │                               │
├──────────────┤    ├───────────────────────────────┤
│              │    │                               │
│ wallets/     │    │  Via RPC Provider:            │
│ ├─ w1.json   │    │  ├─ Infura                    │
│ ├─ w2.json   │    │  ├─ Alchemy                   │
│ └─ ...       │    │  └─ Custom Node               │
│              │    │                               │
│ 🔐 Encrypted │    │  ┌─────────────────────────┐  │
│ Private Keys │    │  │  Ethereum Network       │  │
│              │    │  │  ├─ Smart Contracts     │  │
│              │    │  │  ├─ Transactions        │  │
│              │    │  │  ├─ Balances            │  │
│              │    │  │  └─ State               │  │
│              │    │  └─────────────────────────┘  │
└──────────────┘    └───────────────────────────────┘
```

### Data Flow Example: Creating a Wallet

```
┌──────────┐
│  Client  │
└────┬─────┘
     │
     │ POST /api/v1/wallet/create
     │ {"wallet_name": "my_wallet"}
     ▼
┌─────────────────────────────────────────┐
│  API Layer (routes.py)                  │
│  ├─ Validate request (Pydantic)         │
│  ├─ Extract wallet_name                 │
│  └─ Call wallet_manager.create_wallet() │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  Wallet Manager (secure_execution.py)   │
│                                         │
│  Step 1: Generate Keypair              │
│  ├─ from eth_account import Account    │
│  └─ account = Account.create()         │
│      • private_key: 64 hex chars       │
│      • address: 0x... (42 chars)       │
│                                         │
│  Step 2: Encrypt Private Key           │
│  ├─ Generate random salt (16 bytes)    │
│  ├─ Derive key from password (PBKDF2)  │
│  │   • 100,000 iterations              │
│  │   • SHA-256 hashing                 │
│  ├─ Encrypt with Fernet (AES-128)      │
│  └─ encrypted_key = cipher.encrypt()   │
│                                         │
│  Step 3: Save to File                  │
│  ├─ Create JSON structure               │
│  ├─ {                                   │
│  │    "address": "0x...",              │
│  │    "encrypted_private_key": "...",  │
│  │    "salt": "...",                   │
│  │    "version": "1.0"                 │
│  │  }                                  │
│  └─ Save to wallets/my_wallet.json     │
│                                         │
│  Step 4: Return Info                   │
│  └─ return {                            │
│       "address": "0x...",               │
│       "wallet_name": "my_wallet",       │
│       "network": "sepolia"              │
│     }                                   │
└────────────┬────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────┐
│  API Layer (routes.py)                  │
│  └─ Format response                     │
└────────────┬────────────────────────────┘
             │
             │ 200 OK
             │ {
             │   "address": "0x742d35Cc...",
             │   "wallet_name": "my_wallet",
             │   "network": "sepolia",
             │   "message": "Wallet created!"
             │ }
             ▼
      ┌──────────┐
      │  Client  │
      └──────────┘
```

### Data Flow Example: Checking Balance

```
Client → API → Wallet Manager → Web3 Manager → RPC → Blockchain
                     ↓
               Get address
                     ↓
                              → Build request
                                      ↓
                                   Call eth_getBalance
                                      ↓
                              ← Balance in wei
                     ↓
               Convert wei→ether
                     ↓
Client ← API ← Format response
```

**Detailed Steps:**

1. **Client Request**
   ```http
   GET /api/v1/wallet/balance
   ```

2. **API Layer** (`routes.py`)
   - Receives request
   - Calls `wallet_manager.get_balance()`

3. **Wallet Manager** (`secure_execution.py`)
   - Gets current wallet address
   - Calls `web3_manager.get_balance(address)`

4. **Web3 Manager** (`web3_connection.py`)
   - Converts address to checksum format
   - Calls `self.w3.eth.get_balance(address)`

5. **RPC Provider** (Infura/Alchemy)
   - Makes `eth_getBalance` JSON-RPC call
   - Returns balance in wei

6. **Web3 Manager**
   - Receives balance: `1500000000000000000 wei`
   - Converts: `1.5 ETH`
   - Returns data

7. **API Layer**
   - Formats response:
   ```json
   {
     "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
     "balance_wei": 1500000000000000000,
     "balance_ether": 1.5,
     "currency": "ETH",
     "network": "sepolia"
   }
   ```

8. **Client**
   - Receives and displays balance

---

## 🔧 Core Components

### 1. FastAPI Application (`src/api/main.py`)

**Purpose**: Main application server

**Key Features**:
- Async lifecycle management
- Global state for Web3 and Wallet managers
- CORS configuration
- Comprehensive logging

**Lifecycle**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP
    web3_manager = Web3Manager()
    await web3_manager.connect()  # Connect to blockchain
    
    wallet_manager = WalletManager(web3_manager)
    
    app.state.web3_manager = web3_manager
    app.state.wallet_manager = wallet_manager
    
    yield  # Application runs
    
    # SHUTDOWN
    await web3_manager.disconnect()  # Clean up
```

### 2. API Routes (`src/api/routes.py`)

**Purpose**: Define HTTP endpoints

**Pattern**:
```python
@router.post("/wallet/create")
async def create_wallet(request: Request, body: WalletCreateRequest):
    # 1. Auto-validate input (Pydantic)
    # 2. Get manager from app state
    # 3. Call business logic
    # 4. Handle errors
    # 5. Return formatted response
```

**Pydantic Models**:
- Automatic validation
- Type safety
- Auto-generated documentation
- Clear error messages

### 3. Web3 Manager (`src/execution/web3_connection.py`)

**Purpose**: Interface with blockchain networks

**Supported Networks**:
```python
SUPPORTED_NETWORKS = {
    "sepolia": {
        "name": "Sepolia Testnet",
        "chain_id": 11155111,
        "currency": "ETH"
    },
    "polygon_mumbai": {
        "name": "Polygon Mumbai",
        "chain_id": 80001,
        "currency": "MATIC"
    },
    "ethereum": {
        "name": "Ethereum Mainnet",
        "chain_id": 1,
        "currency": "ETH"
    },
    "polygon": {
        "name": "Polygon Mainnet",
        "chain_id": 137,
        "currency": "MATIC"
    }
}
```

**Key Methods**:
- `connect()` - Establish RPC connection
- `is_connected()` - Check connection status
- `get_balance(address)` - Query balance
- `get_transaction(hash)` - Get transaction details
- `get_network_info()` - Network metadata

### 4. Wallet Manager (`src/execution/secure_execution.py`)

**Purpose**: Secure wallet operations

**Encryption Process**:
```
Password ("my_password")
    │
    ▼
┌───────────────────┐
│ PBKDF2-HMAC       │
│ • Algorithm: SHA256│
│ • Iterations: 100k │
│ • Salt: 16 bytes   │
└─────────┬─────────┘
          │
          ▼
   Derived Key (32 bytes)
          │
          ▼
┌───────────────────┐
│ Fernet Cipher     │
│ • AES-128 in CBC  │
│ • HMAC for auth   │
│ • Timestamp       │
└─────────┬─────────┘
          │
          ▼
Private Key (plain) → Encrypted Data
          │
          ▼
   Store in JSON file
```

**Key Methods**:
- `create_wallet(name)` - Generate and encrypt new wallet
- `load_wallet(name)` - Decrypt and load existing wallet
- `get_balance()` - Check balance via Web3
- `list_wallets()` - List available wallets

---

## 🔐 Security Implementation

### Layer 1: Transport Security
- HTTPS (in production)
- CORS policies
- Rate limiting (future)

### Layer 2: API Security
- Input validation (Pydantic)
- Type checking
- SQL injection prevention (no SQL in Phase 1)
- XSS prevention
- Error handling (no sensitive data in errors)

### Layer 3: Application Security
- Environment-based configuration
- No hardcoded secrets
- Secure logging (no key exposure)
- Principle of least privilege

### Layer 4: Cryptographic Security

**PBKDF2-HMAC (Key Derivation)**:
```python
kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,                    # 256-bit key
    salt=os.urandom(16),          # Random salt per wallet
    iterations=100000,            # Slow! (~100ms)
    backend=default_backend()
)
derived_key = kdf.derive(password.encode())
```

**Why 100,000 iterations?**
- Makes brute-force attacks impractical
- ~100ms per attempt = 10 attempts/second
- To try 1 million passwords: ~27 hours
- Industry standard for password-based encryption

**Fernet (Symmetric Encryption)**:
- AES-128 in CBC mode
- HMAC for authentication (tamper detection)
- Includes timestamp
- Part of Python's `cryptography` library

**Key Storage**:
```json
{
  "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
  "encrypted_private_key": "gAAAAABh...",
  "salt": "aGVsbG8gd29ybGQ=",
  "version": "1.0"
}
```

### Layer 5: Storage Security
- Encrypted wallet files
- `.gitignore` prevents commits
- Separate from application code
- File permissions (600 recommended)

---

## 💻 Technology Choices

### Why Python?
✅ **Pros**:
- Huge ecosystem (Web3, crypto, AI libraries)
- Excellent Web3.py library
- Easy async/await support
- Rapid development
- Perfect for AI/ML integration (future phases)

❌ **Alternatives**:
- **JavaScript/TypeScript**: Good Web3 support, but less mature crypto libraries
- **Go**: Fast, but smaller ecosystem for rapid prototyping
- **Rust**: Maximum security, but steeper learning curve

### Why FastAPI?
✅ **Pros**:
- Fastest Python framework (Starlette + Pydantic)
- Auto-generated interactive documentation
- Async/await native support
- Type hints everywhere
- Perfect for AI integration (JSON API)

❌ **Alternatives**:
- **Flask**: Older, synchronous, no auto-docs
- **Django**: Too heavy for API-only project
- **Starlette**: Lower-level, more boilerplate

### Why Web3.py?
✅ **Pros**:
- Official Ethereum Python library
- Mature and battle-tested
- Comprehensive documentation
- Active development
- Supports all EVM chains

❌ **Alternatives**:
- **ethers.js** (JavaScript): Great, but wrong language
- **Custom RPC**: Too much work, reinventing the wheel

### Why Cryptography Library?
✅ **Pros**:
- Industry standard
- Well-audited
- Fernet (easy symmetric encryption)
- PBKDF2-HMAC built-in
- Active security updates

❌ **Alternatives**:
- **PyCrypto**: Deprecated, security issues
- **hashlib only**: Need to implement encryption
- **Custom**: Never roll your own crypto!

---

## 🔄 Request Lifecycle

### Complete Request Flow

```
1. HTTP Request arrives
   ↓
2. Uvicorn receives (ASGI server)
   ↓
3. FastAPI routing (match endpoint)
   ↓
4. Middleware processing (CORS, etc.)
   ↓
5. Pydantic validation (automatic)
   ↓
6. Endpoint function called
   ↓
7. Business logic execution
   │  ├─ Wallet Manager
   │  └─ Web3 Manager
   ↓
8. Response formatting
   ↓
9. JSON serialization
   ↓
10. HTTP Response sent
```

### Error Handling Flow

```
Exception occurs
   ↓
Caught by FastAPI
   ↓
Logged (no sensitive data)
   ↓
Format user-friendly error
   ↓
Return appropriate HTTP status
   │
   ├─ 400: Bad Request (validation failed)
   ├─ 404: Not Found (wallet doesn't exist)
   ├─ 500: Internal Error (unexpected)
   └─ 503: Service Unavailable (Web3 down)
```

---

## 🔮 Future Architecture (Phases 2-6)

### Phase 2: Transaction Execution

```
┌─────────────────┐
│ Transaction     │
│ Builder         │
│ ├─ Gas estimate │
│ ├─ Nonce mgmt   │
│ └─ TX signing   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Broadcast       │
│ ├─ Submit TX    │
│ ├─ Monitor      │
│ └─ Confirm      │
└─────────────────┘
```

### Phase 3: Rule & Risk Engine

```
Transaction Request
   ↓
┌─────────────────────┐
│ Rule Engine         │
│ ├─ Spending limits  │
│ ├─ Whitelists       │
│ ├─ Risk scoring     │
│ └─ Approval flow    │
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    ▼           ▼
 ALLOW      REQUIRE_APPROVAL
    │           │
    ▼           ▼
 Execute     Wait for human
```

### Phase 4: AI Integration

```
AI Agent (natural language)
"Send 0.1 ETH to Alice"
   ↓
┌───────────────────┐
│ Intent Parser     │
│ ├─ NLP processing │
│ ├─ Entity extract │
│ └─ Validation     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ Transaction       │
│ Simulator         │
│ (dry run)         │
└─────────┬─────────┘
          │
          ▼
     Confirmation?
          │
          ▼
      Execute
```

### Phase 5: Dashboard

```
┌──────────────────────────┐
│ Web Dashboard            │
│ ┌──────────────────────┐ │
│ │ Real-time Activity   │ │
│ │ • Pending TX         │ │
│ │ • Balances           │ │
│ │ • Alerts             │ │
│ └──────────────────────┘ │
│ ┌──────────────────────┐ │
│ │ Rule Management      │ │
│ │ • Edit rules         │ │
│ │ • Approval queue     │ │
│ └──────────────────────┘ │
│ ┌──────────────────────┐ │
│ │ Analytics            │ │
│ │ • Spending graphs    │ │
│ │ • Transaction history│ │
│ └──────────────────────┘ │
└──────────────────────────┘
```

### Complete Future System

```
┌─────────────────────────────────────────────────────────┐
│                    AI AGENT LAYER                       │
│  ChatGPT, Claude, Custom Bots, Voice Assistants         │
└────────────────────┬────────────────────────────────────┘
                     │ Natural Language / JSON
                     ▼
┌─────────────────────────────────────────────────────────┐
│                AI INTEGRATION LAYER (Phase 4)           │
│  ├─ Intent Parsing                                      │
│  ├─ Entity Extraction                                   │
│  └─ Context Management                                  │
└────────────────────┬────────────────────────────────────┘
                     │ Structured Request
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  RULE ENGINE (Phase 3)                  │
│  ├─ Spending Limits                                     │
│  ├─ Whitelist/Blacklist                                 │
│  ├─ Risk Scoring                                        │
│  └─ Approval Workflows                                  │
└────────────────────┬────────────────────────────────────┘
                     │ Validated Request
                     ▼
┌─────────────────────────────────────────────────────────┐
│              TRANSACTION ENGINE (Phase 2)               │
│  ├─ Gas Estimation                                      │
│  ├─ Transaction Building                                │
│  ├─ Signing                                             │
│  └─ Broadcasting                                        │
└────────────────────┬────────────────────────────────────┘
                     │
      ┌──────────────┼──────────────┐
      │              │              │
      ▼              ▼              ▼
┌──────────┐   ┌──────────┐   ┌────────────┐
│ Wallet   │   │  Web3    │   │  Audit     │
│ Manager  │   │ Manager  │   │  Logger    │
│ (Phase 1)│   │(Phase 1) │   │ (Phase 2)  │
└────┬─────┘   └────┬─────┘   └──────┬─────┘
     │              │                 │
     ▼              ▼                 ▼
 [Storage]     [Blockchain]      [Database]
```

---

## 📊 Key Concepts Explained

### What is RPC?
**Remote Procedure Call** - A protocol where your app calls functions on a remote server.

For blockchains:
- Your app → RPC Provider (Infura/Alchemy) → Blockchain nodes
- Instead of running your own node (expensive, complex)
- Pay per request or free tier

### What is Web3?
The technology stack for decentralized applications:
- **Web 1.0**: Read-only (static websites)
- **Web 2.0**: Read-write (social media, user content)
- **Web 3.0**: Read-write-own (blockchain, user ownership)

### What is EVM?
**Ethereum Virtual Machine** - The runtime environment for smart contracts.

EVM-compatible chains:
- Ethereum
- Polygon
- Avalanche
- Arbitrum
- Optimism
- BSC
- And many more...

All use the same API, so ChainPilot works with all of them!

### Wei vs Ether
- **Wei**: Smallest unit (like cents)
- **Ether**: Main unit (like dollars)
- **Conversion**: 1 ETH = 1,000,000,000,000,000,000 wei (10^18)

---

## ✅ System Design Principles

1. **Modularity**: Each component has one job
2. **Security First**: Multiple layers of protection
3. **Scalability**: Easy to add features
4. **Testability**: Each component can be tested independently
5. **Maintainability**: Clear structure, good documentation
6. **Developer Friendly**: Type hints, auto-docs, clear errors

---

**Next Steps**: See `ROADMAP.md` for development phases

**Status**: Phase 1 Complete ✅ | All core systems operational
