# Architecture & System Design

This document provides a detailed overview of the system architecture for **AI Banking Bridge**, including the workflow, components, security layers, and internal interactions.

---

## 🏛️ High-Level Architecture
The system is composed of four core layers:

```

AI Agent
↓
AI Proxy API
↓
Rule & Risk Engine
↓
Secure Execution Layer
↓
Banking / Crypto Rail

```

### **1. AI Proxy API**
This is the only interface visible to the agent.

Responsibilities:
- Receives requests from the AI agent (JSON-based)
- Validates schema and intent
- Converts natural-language reasoning into structured actions
- Applies baseline guardrails to avoid malformed or unsafe requests

Key endpoints:
- `POST /transaction/simulate`
- `POST /transaction/execute`
- `GET /accounts`
- `GET /budget`

The API is designed with:
- LLM-friendly formatting
- deterministically structured responses
- ambiguity resolution hints for the agent

---

## ⚖️ Rule & Risk Engine
The decision-making layer that evaluates all transaction attempts.

Responsibilities:
- Budget checks
- Spending limits (daily, weekly, per-category)
- Risk classification (normal, anomalous, dangerous)
- Human-in-the-loop triggers
- Conditional rules created by the user

Examples of rules:
- "Maximum transaction: 50€ unless tagged as recurring billing"
- "If transaction > 100€, pause and request confirmation"
- "Only allow whitelisted crypto addresses"

The engine outputs one of three decisions:
- **ALLOW** → execution proceeds
- **ALLOW_WITH_CONFIRMATION** → dashboard notification
- **DENY** → logged and blocked

---

## 🔐 Secure Execution Layer
The most sensitive part of the system.

Responsibilities:
- Holds encrypted private keys (crypto)
- Interfaces with PSD2/Open Banking providers (banking)
- Signs and broadcasts transactions
- Ensures isolation of credentials from the AI agent

Security Techniques Used:
- Hardware Security Module (HSM)-like storage or MPC wallets
- Transaction sandboxing
- Tamper-proof logs
- Non-exportable signing keys

Supported rails:

### **Crypto (Web3)**
- EVM wallets (Ethereum, Polygon, etc.)
- MPC wallets for multi-device signing
- Stablecoins for reliable value

### **Banking (PSD2)**
- Account info
- Payment initiation
- Balance checks

---

## 📊 Dashboard & Monitoring
A minimalistic black/white interface that allows users to:
- View all agent activity
- Inspect transaction history
- Monitor budgets and spending trends
- Review pending approvals
- Set spending rules
- Export logs

Dashboard elements:
- **Graphs**: daily spend, spending categories, risk heatmap
- **Latest agent requests**: timestamp, intent, decision
- **KPIs**: success rate, average spend per task
- **Security alerts**: unusual behavior, risk flags

---

## 🔄 Workflow Example
Here’s a full example of the system in action:

1. **AI agent forms an intent** (e.g., "buy hosting credits for 20€")
2. It sends a request → `POST /transaction/execute`
3. The API validates structure
4. The Rule Engine evaluates limits
5. The transaction is classified as low-risk
6. Execution Layer signs a crypto tx or triggers a PSD2 payment
7. Dashboard logs everything and updates graphs

---

## 🧱 Key Architectural Principles
- **Safety-first**: All operations are mediated by deterministic rules
- **Separation of concerns**: AI cannot access sensitive keys
- **Auditability**: Every action is logged and inspectable
- **Extensibility**: New AI agents, banks, and chains can be added easily
- **LLM-native design**: Friendly formats and predictable responses

---

## 🔮 Future Extensions
- AI-generated spending rules
- Shared multi-user accounts
- Deep anomaly detection on agent behavior
- Smart contract programmable spending wallets
- Payment batching and gas optimization

---
