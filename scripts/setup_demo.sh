#!/bin/bash

# ChainPilot Demo Setup Script
# Helps you set up for a live blockchain demo

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║            🎬 ChainPilot Live Demo Setup                      ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if .env exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Overwrite? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

echo "📋 Let's set up your live demo configuration..."
echo ""

# Get RPC URL
echo "1️⃣  RPC URL Configuration"
echo "   Need a free RPC URL? Try:"
echo "   - Alchemy: https://www.alchemy.com/ (recommended)"
echo "   - Infura: https://infura.io/"
echo ""
read -p "Enter your RPC URL (Sepolia): " RPC_URL

if [ -z "$RPC_URL" ]; then
    echo "❌ RPC URL is required!"
    exit 1
fi

# Choose network
echo ""
echo "2️⃣  Network Selection"
echo "   1) Sepolia Testnet (recommended for demo)"
echo "   2) Mumbai Testnet (Polygon)"
echo "   3) Goerli Testnet"
echo ""
read -p "Select network (1-3): " NETWORK_CHOICE

case $NETWORK_CHOICE in
    1)
        CHAIN_ID=11155111
        NETWORK_NAME="sepolia"
        echo "✅ Using Sepolia Testnet"
        echo "   Get free ETH: https://sepoliafaucet.com/"
        ;;
    2)
        CHAIN_ID=80001
        NETWORK_NAME="mumbai"
        echo "✅ Using Mumbai Testnet"
        echo "   Get free MATIC: https://faucet.polygon.technology/"
        ;;
    3)
        CHAIN_ID=5
        NETWORK_NAME="goerli"
        echo "✅ Using Goerli Testnet"
        echo "   Get free ETH: https://goerlifaucet.com/"
        ;;
    *)
        echo "❌ Invalid choice!"
        exit 1
        ;;
esac

# Security level
echo ""
echo "3️⃣  Security Level"
echo "   1) MODERATE (recommended for demos)"
echo "   2) STRICT (production-like)"
echo "   3) LOCKDOWN (maximum security)"
echo ""
read -p "Select security level (1-3): " SECURITY_CHOICE

case $SECURITY_CHOICE in
    1)
        SECURITY_LEVEL="MODERATE"
        echo "✅ MODERATE security (good for demos)"
        ;;
    2)
        SECURITY_LEVEL="STRICT"
        echo "✅ STRICT security (production-like)"
        ;;
    3)
        SECURITY_LEVEL="LOCKDOWN"
        echo "✅ LOCKDOWN security (requires approval for everything)"
        ;;
    *)
        echo "❌ Invalid choice!"
        exit 1
        ;;
esac

# Create .env file
echo ""
echo "📝 Creating .env file..."
cat > .env << EOF
# ChainPilot Live Demo Configuration
# Generated: $(date)

# Network Configuration
CHAINPILOT_RPC_URL=$RPC_URL
CHAINPILOT_CHAIN_ID=$CHAIN_ID
CHAINPILOT_NETWORK_NAME=$NETWORK_NAME

# Security Configuration
CHAINPILOT_SECURITY_LEVEL=$SECURITY_LEVEL
CHAINPILOT_SANDBOX_MODE=false  # REAL transactions!

# Custom Limits (optional - adjust as needed)
# CHAINPILOT_MAX_SINGLE_TX=0.1
# CHAINPILOT_HOURLY_LIMIT=0.5
# CHAINPILOT_DAILY_LIMIT=2.0

# Demo Configuration
CHAINPILOT_AUTO_APPROVE=false  # Set to true for automated demos
EOF

echo "✅ .env file created successfully!"
echo ""

# Verify setup
echo "🔍 Verifying setup..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    exit 1
fi
echo "✅ Python 3 found"

# Check dependencies
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found!"
    exit 1
fi
echo "✅ requirements.txt found"

# Check if venv exists
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found"
    read -p "Create virtual environment? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        python3 -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
        echo "✅ Virtual environment created and dependencies installed"
    fi
else
    echo "✅ Virtual environment found"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ Setup Complete!                          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Get testnet funds:"
if [ "$NETWORK_NAME" = "sepolia" ]; then
    echo "   • Visit: https://sepoliafaucet.com/"
elif [ "$NETWORK_NAME" = "mumbai" ]; then
    echo "   • Visit: https://faucet.polygon.technology/"
else
    echo "   • Visit: https://goerlifaucet.com/"
fi
echo "   • Send to your wallet address"
echo "   • Wait for confirmation (~30 seconds)"
echo ""
echo "2️⃣  Start the server:"
echo "   $ python3 run.py"
echo ""
echo "3️⃣  Open dashboard:"
echo "   🌐 http://localhost:8000/"
echo ""
echo "4️⃣  Create or import wallet:"
echo "   # Option A: Create new wallet"
echo "   $ curl -X POST http://localhost:8000/api/v1/wallet/create \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"wallet_name\": \"demo_wallet\"}'"
echo ""
echo "   # Option B: Import existing wallet (advanced)"
echo "   See DEMO_GUIDE.md for instructions"
echo ""
echo "5️⃣  Send test transaction:"
echo "   $ curl -X POST http://localhost:8000/api/v1/transaction/send \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"to_address\": \"0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7\", \"value\": 0.01}'"
echo ""
echo "📚 For complete demo guide, see: DEMO_GUIDE.md"
echo ""
echo "⚠️  REMEMBER:"
echo "   • You're using REAL blockchain ($NETWORK_NAME testnet)"
echo "   • Transactions are permanent"
echo "   • Start with small amounts (0.01 ETH)"
echo "   • Keep your private keys secure"
echo ""
echo "🚀 Ready for live demo!"
echo ""

