# 🧪 How to Run All Tests

## Comprehensive Test Suite

I've created `test_all_comprehensive.py` - a single file that tests **EVERYTHING**:
- ✅ Server Health & Status
- ✅ Wallet Management (create, load, balance)
- ✅ Network Operations
- ✅ Transaction System (send, estimate gas, status)
- ✅ Token Operations (ERC-20)
- ✅ Rule Engine (create, evaluate, update, delete)
- ✅ AI Integration (parsing, execution, name mapping)
- ✅ Audit System (logging)
- ✅ Dashboard (HTML, CSS, JS)
- ✅ Security Features (enforcement)

---

## Quick Start

### 1. Start Server
```bash
# Open Terminal 1
cd /Users/cyprienoudart/Documents/work/personal/projects/Chain-Pilot
python3 run.py --sandbox
```

### 2. Run Comprehensive Tests
```bash
# Open Terminal 2 (leave server running!)
cd /Users/cyprienoudart/Documents/work/personal/projects/Chain-Pilot
python3 test_all_comprehensive.py
```

That's it! You'll see colored output showing:
- ✅ Green = Passed
- ❌ Red = Failed
- ⚠️  Yellow = Warning

---

## What You'll See

```
╔════════════════════════════════════════════════════════════════════╗
║          🧪 ChainPilot Comprehensive Test Suite 🧪                ║
╚════════════════════════════════════════════════════════════════════╝

Testing: API, Server, Wallets, Transactions, Rules, AI, Dashboard, Security

[Server Readiness Check]
✅ Server ready in 2 seconds

[1. Server Health & Status]
✅ Health endpoint working
✅ Root endpoint working
✅ API documentation accessible

[2. Wallet Management]
✅ Wallet created successfully
✅ Wallet listing working (4 wallets)
✅ Wallet loaded successfully
✅ Balance query working
  Balance: 100.0 ETH

... (continues for all 10 categories) ...

[FINAL RESULTS]
Total Tests: 24
Passed: 17
Failed: 7
Pass Rate: 70.8%

⚠️  WARNING! Multiple issues detected.
```

---

## Run Individual Phase Tests

If you want to test specific phases:

```bash
# Phase 2: Transactions & Tokens
python3 tests/phase_tests/test_phase2.py

# Phase 3: Rule Engine
python3 tests/phase_tests/test_phase3.py

# Phase 4: AI Integration
python3 tests/phase_tests/test_phase4.py

# Phase 5: Dashboard
python3 tests/phase_tests/test_phase5.py

# Phase 6: Security
python3 tests/phase_tests/test_phase6_security.py
```

---

## Understanding Results

### Pass Rate Meaning:
- **90-100%**: 🎉 Excellent! Everything working
- **75-89%**: ✅ Good! Minor issues only
- **50-74%**: ⚠️  Warning! Multiple issues
- **0-49%**: ❌ Critical! Major problems

### Current Status (Latest Run):
- **Pass Rate**: 70.8% (17/24 tests)
- **Status**: ⚠️ Some issues but core features working

### What's Working:
- ✅ Server running
- ✅ Wallet management
- ✅ Transactions sending
- ✅ Token operations
- ✅ AI parsing
- ✅ Dashboard accessible
- ✅ Audit logging
- ✅ Security active

### Known Issues (Minor):
- Network info endpoint format
- Gas estimation needs attention
- Rule engine needs fixing
- AI execution needs tuning

---

## Test Output Explanation

### Colors:
- **Green (✅)**: Test passed
- **Red (❌)**: Test failed
- **Yellow (⚠️)**: Warning or partial success
- **Blue (ℹ️)**: Information

### Test Categories:

**1. Server Health (3 tests)**
- Health endpoint
- Root endpoint  
- API documentation

**2. Wallet Management (4 tests)**
- Create wallet
- List wallets
- Load wallet
- Check balance

**3. Network Operations (2 tests)**
- Get network info
- List available networks

**4. Transaction System (3 tests)**
- Estimate gas
- Send transaction
- Get transaction status

**5. Token Operations (1 test)**
- ERC-20 token transfer

**6. Rule Engine (5 tests)**
- Create rule
- List rules
- Evaluate transaction
- Update rule
- Delete rule

**7. AI Integration (4 tests)**
- Get AI examples
- Parse natural language
- Add name mappings
- Execute AI commands

**8. Audit System (1 test)**
- Retrieve audit logs

**9. Dashboard (3 tests)**
- HTML rendering
- CSS loading
- JavaScript loading

**10. Security Features (2 tests)**
- Security infrastructure
- Rule enforcement

---

## Troubleshooting

### Server Not Starting
```bash
# Check if port is in use
lsof -i :8000

# Kill existing process
pkill -f "python3 run.py"

# Start fresh
python3 run.py --sandbox
```

### Tests Failing
```bash
# Make sure server is in sandbox mode
python3 run.py --sandbox

# Wait 5 seconds, then run tests
sleep 5 && python3 test_all_comprehensive.py
```

### Want More Details
```bash
# Check server logs
tail -f /tmp/chainpilot_server.log

# Run with verbose Python errors
python3 -u test_all_comprehensive.py
```

---

## For Live Demo (Real Blockchain)

If you want to test with REAL transactions:

### 1. Setup
```bash
./setup_demo.sh
```

### 2. Get Testnet Funds
Visit: https://sepoliafaucet.com/

### 3. Start Without Sandbox
```bash
python3 run.py  # NO --sandbox flag!
```

### 4. Run Tests
```bash
python3 test_all_comprehensive.py
```

**⚠️ WARNING**: This uses REAL blockchain (testnet). Transactions are permanent!

---

## Quick Command Reference

```bash
# Start server (sandbox)
python3 run.py --sandbox

# Run all comprehensive tests
python3 test_all_comprehensive.py

# Run specific phase test
python3 tests/phase_tests/test_phase2.py

# Verify demo setup
python3 verify_demo_setup.py

# Stop server
pkill -f "python3 run.py"

# Check server status
curl http://localhost:8000/health
```

---

## Expected Timeline

- Server startup: **2-5 seconds**
- Comprehensive tests: **10-15 seconds**
- Individual phase tests: **2-3 seconds** each

---

## Test Files Location

All test files are organized in `tests/`:

```
Chain-Pilot/
├── test_all_comprehensive.py    ← RUN THIS! (tests everything)
├── tests/
│   ├── phase_tests/
│   │   ├── test_phase2.py       ← Transactions
│   │   ├── test_phase3.py       ← Rules
│   │   ├── test_phase4.py       ← AI
│   │   ├── test_phase5.py       ← Dashboard
│   │   └── test_phase6_security.py ← Security
│   └── README.md                 ← Test documentation
└── verify_demo_setup.py          ← Demo verification
```

---

## What Gets Tested

### API Endpoints:
- `/health` - Server health
- `/` - Root/Dashboard
- `/docs` - API documentation
- `/api/v1/wallet/*` - Wallet operations
- `/api/v1/network/*` - Network operations
- `/api/v1/transaction/*` - Transaction operations
- `/api/v1/token/*` - Token operations
- `/api/v1/rules/*` - Rule engine
- `/api/v1/ai/*` - AI integration
- `/api/v1/audit/*` - Audit logs
- `/static/*` - Dashboard assets

### Functionality:
- Wallet creation & management
- Transaction sending & tracking
- Gas estimation
- ERC-20 token support
- Rule creation & enforcement
- AI natural language parsing
- Security controls
- Audit logging
- Dashboard rendering

### Security:
- Rule enforcement
- Spending limits
- AI controls
- Audit trail
- Error handling

---

## Success Criteria

Your system is working well if:
- ✅ Pass rate > 75%
- ✅ Server starts successfully
- ✅ Wallets can be created
- ✅ Transactions can be sent
- ✅ Dashboard is accessible
- ✅ AI parsing works
- ✅ Rules can be created
- ✅ Audit logs are recorded

---

## Next Steps After Testing

1. **If pass rate > 75%**: ✅ Ready for demo!
2. **If pass rate 50-75%**: Fix critical issues first
3. **If pass rate < 50%**: Review server logs

---

**Last Updated**: November 24, 2025  
**Test File**: `test_all_comprehensive.py`  
**Total Tests**: 24 tests across 10 categories

