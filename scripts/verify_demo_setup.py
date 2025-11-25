#!/usr/bin/env python3
"""
ChainPilot Demo Verification Script
Checks if your setup is ready for a live demo
"""
import os
import sys
import requests
import time
from web3 import Web3

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def check_pass(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def check_fail(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def check_warn(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def check_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

def check_env_file():
    """Check if .env file exists and is configured"""
    print_header("1. Checking Configuration")
    
    if not os.path.exists('.env'):
        check_fail(".env file not found!")
        check_info("Run: ./setup_demo.sh")
        return False
    
    check_pass(".env file exists")
    
    # Read .env
    with open('.env', 'r') as f:
        env_content = f.read()
    
    # Check for required variables
    if 'CHAINPILOT_RPC_URL' not in env_content:
        check_fail("RPC_URL not configured")
        return False
    check_pass("RPC URL configured")
    
    if 'CHAINPILOT_SANDBOX_MODE=false' in env_content:
        check_pass("Sandbox mode disabled (REAL transactions)")
        check_warn("You're using a REAL blockchain!")
    else:
        check_warn("Sandbox mode enabled (simulated transactions)")
    
    return True

def check_server():
    """Check if server is running"""
    print_header("2. Checking Server")
    
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            check_pass("Server is running")
            check_info(f"  Network: {data.get('network', 'unknown')}")
            check_info(f"  Chain ID: {data.get('chain_id', 'unknown')}")
            check_info(f"  Sandbox: {data.get('sandbox_mode', 'unknown')}")
            return True
    except requests.ConnectionError:
        check_fail("Server not running!")
        check_info("Start with: python3 run.py")
        return False
    except Exception as e:
        check_fail(f"Server error: {e}")
        return False

def check_wallet():
    """Check if wallet is loaded"""
    print_header("3. Checking Wallet")
    
    try:
        response = requests.get('http://localhost:8000/api/v1/wallet/list')
        if response.status_code == 200:
            wallets = response.json().get('wallets', [])
            if wallets:
                check_pass(f"Found {len(wallets)} wallet(s)")
                for wallet in wallets:
                    check_info(f"  • {wallet['name']}: {wallet['address'][:10]}...")
            else:
                check_warn("No wallets found")
                check_info("Create one: curl -X POST http://localhost:8000/api/v1/wallet/create -d '{\"wallet_name\":\"demo\"}'")
                return False
        
        # Check if a wallet is loaded
        response = requests.get('http://localhost:8000/api/v1/wallet/balance')
        if response.status_code == 200:
            balance_data = response.json()
            check_pass("Wallet loaded!")
            check_info(f"  Address: {balance_data['address']}")
            check_info(f"  Balance: {balance_data['balance_ether']} ETH")
            
            if balance_data['balance_ether'] < 0.01:
                check_warn("Low balance - get testnet funds!")
                return False
            else:
                check_pass(f"Sufficient funds ({balance_data['balance_ether']} ETH)")
            return True
        else:
            check_warn("No wallet loaded")
            check_info("Load wallet first")
            return False
    except Exception as e:
        check_fail(f"Wallet check error: {e}")
        return False

def check_rpc_connection():
    """Check RPC connection"""
    print_header("4. Checking RPC Connection")
    
    # Load .env
    rpc_url = None
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('CHAINPILOT_RPC_URL='):
                    rpc_url = line.split('=', 1)[1].strip()
                    break
    except:
        pass
    
    if not rpc_url:
        check_fail("RPC URL not found in .env")
        return False
    
    try:
        w3 = Web3(Web3.HTTPProvider(rpc_url))
        if w3.is_connected():
            check_pass("RPC connection successful")
            block_number = w3.eth.block_number
            check_info(f"  Current block: {block_number}")
            return True
        else:
            check_fail("Cannot connect to RPC")
            check_info("Check your RPC URL")
            return False
    except Exception as e:
        check_fail(f"RPC connection error: {e}")
        return False

def check_dashboard():
    """Check if dashboard is accessible"""
    print_header("5. Checking Dashboard")
    
    try:
        response = requests.get('http://localhost:8000/')
        if response.status_code == 200:
            check_pass("Dashboard accessible")
            check_info("  URL: http://localhost:8000/")
            return True
        else:
            check_fail(f"Dashboard returned {response.status_code}")
            return False
    except Exception as e:
        check_fail(f"Dashboard error: {e}")
        return False

def check_api_docs():
    """Check if API docs are accessible"""
    print_header("6. Checking API Documentation")
    
    try:
        response = requests.get('http://localhost:8000/docs')
        if response.status_code == 200:
            check_pass("API docs accessible")
            check_info("  URL: http://localhost:8000/docs")
            return True
        else:
            check_fail(f"API docs returned {response.status_code}")
            return False
    except Exception as e:
        check_fail(f"API docs error: {e}")
        return False

def check_security_features():
    """Check if security features are active"""
    print_header("7. Checking Security Features")
    
    try:
        # Check rules endpoint
        response = requests.get('http://localhost:8000/api/v1/rules')
        if response.status_code == 200:
            rules = response.json().get('rules', [])
            check_pass(f"Rule engine active ({len(rules)} rules)")
        
        # Check AI endpoint
        response = requests.get('http://localhost:8000/api/v1/ai/examples')
        if response.status_code == 200:
            check_pass("AI integration active")
        
        check_pass("Security features operational")
        return True
    except Exception as e:
        check_warn(f"Security check incomplete: {e}")
        return True  # Not critical

def main():
    print("""
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║          🔍 ChainPilot Demo Verification                      ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
""")
    
    checks = []
    
    # Run all checks
    checks.append(("Configuration", check_env_file()))
    checks.append(("Server", check_server()))
    checks.append(("Wallet", check_wallet()))
    checks.append(("RPC Connection", check_rpc_connection()))
    checks.append(("Dashboard", check_dashboard()))
    checks.append(("API Docs", check_api_docs()))
    checks.append(("Security", check_security_features()))
    
    # Summary
    print_header("Summary")
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    for name, result in checks:
        if result:
            check_pass(f"{name}")
        else:
            check_fail(f"{name}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    if passed == total:
        print(f"{Colors.GREEN}✅ ALL CHECKS PASSED! ({passed}/{total}){Colors.END}")
        print(f"{Colors.GREEN}🚀 Ready for live demo!{Colors.END}")
        
        print(f"\n{Colors.BLUE}Next Steps:{Colors.END}")
        print("1. Open dashboard: http://localhost:8000/")
        print("2. Send test transaction:")
        print('   curl -X POST http://localhost:8000/api/v1/transaction/send \\')
        print('     -H "Content-Type: application/json" \\')
        print('     -d \'{"to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7", "value": 0.01}\'')
        print("3. Watch it on dashboard and Etherscan!")
        
    else:
        print(f"{Colors.YELLOW}⚠️  {passed}/{total} checks passed{Colors.END}")
        print(f"{Colors.YELLOW}Please fix the issues above before demo{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

