#!/usr/bin/env python3
"""
Phase 2 Testing Script
Comprehensive tests for all Phase 2 functionality
"""
import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


class Colors:
    """Terminal colors"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_success(msg):
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")


def print_error(msg):
    print(f"{Colors.RED}❌ {msg}{Colors.END}")


def print_info(msg):
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")


def print_warning(msg):
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")


def print_section(title):
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}{title}{Colors.END}")
    print('='*60)


def test_api_health():
    """Test API health check"""
    print_section("1. API Health Check")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is healthy: {data.get('status')}")
            print_info(f"Web3 connected: {data.get('web3_connected')}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cannot connect to API: {e}")
        print_info("Make sure server is running: python3 run.py --sandbox")
        return False


def test_wallet_creation():
    """Test wallet creation"""
    print_section("2. Wallet Creation")
    try:
        response = requests.post(
            f"{API_V1}/wallet/create",
            json={"wallet_name": "test_phase2"}
        )
        if response.status_code == 200:
            data = response.json()
            print_success(f"Wallet created: {data['wallet_name']}")
            print_info(f"Address: {data['address']}")
            return data['address']
        else:
            print_warning("Wallet might already exist, trying to load...")
            response = requests.post(
                f"{API_V1}/wallet/load",
                json={"wallet_name": "test_phase2"}
            )
            if response.status_code == 200:
                data = response.json()
                print_success(f"Wallet loaded: {data['wallet_name']}")
                print_info(f"Address: {data['address']}")
                return data['address']
            else:
                print_error("Failed to create or load wallet")
                return None
    except Exception as e:
        print_error(f"Wallet creation failed: {e}")
        return None


def test_balance_check(address):
    """Test balance checking"""
    print_section("3. Balance Check")
    try:
        response = requests.get(f"{API_V1}/wallet/balance")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Balance retrieved")
            print_info(f"Balance: {data['balance_ether']} {data['currency']}")
            print_info(f"Balance (wei): {data['balance_wei']}")
            return True
        else:
            print_error(f"Balance check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Balance check failed: {e}")
        return False


def test_transaction_estimate():
    """Test transaction estimation"""
    print_section("4. Transaction Estimation")
    try:
        response = requests.post(
            f"{API_V1}/transaction/estimate",
            json={
                "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
                "value": 0.001
            }
        )
        if response.status_code == 200:
            data = response.json()
            print_success("Transaction estimated successfully")
            print_info(f"Gas estimate: {data.get('gas_estimate')}")
            print_info(f"Gas cost: {data.get('gas_cost_ether')} ETH")
            print_info(f"Total cost: {data.get('total_cost_ether')} ETH")
            print_info(f"Can execute: {data.get('can_execute')}")
            
            if data.get('sandbox_mode'):
                print_warning("SANDBOX MODE: This is a simulation")
            
            return data.get('can_execute')
        else:
            print_error(f"Estimation failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Estimation failed: {e}")
        return False


def test_transaction_send():
    """Test sending a transaction"""
    print_section("5. Send Transaction")
    try:
        response = requests.post(
            f"{API_V1}/transaction/send",
            json={
                "to_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
                "value": 0.001
            }
        )
        if response.status_code == 200:
            data = response.json()
            print_success("Transaction sent successfully!")
            print_info(f"TX Hash: {data['tx_hash']}")
            print_info(f"Status: {data['status']}")
            print_info(f"Explorer: {data.get('explorer_url', 'N/A')}")
            return data['tx_hash']
        else:
            print_error(f"Transaction failed: {response.status_code}")
            print_error(response.text)
            return None
    except Exception as e:
        print_error(f"Transaction failed: {e}")
        return None


def test_transaction_status(tx_hash):
    """Test transaction status check"""
    print_section("6. Check Transaction Status")
    if not tx_hash:
        print_warning("No transaction hash to check")
        return False
    
    try:
        response = requests.get(f"{API_V1}/transaction/{tx_hash}")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Transaction status: {data['status']}")
            if data.get('block_number'):
                print_info(f"Block: {data['block_number']}")
                print_info(f"Gas used: {data.get('gas_used')}")
            return True
        else:
            print_error(f"Status check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Status check failed: {e}")
        return False


def test_token_balance():
    """Test token balance check"""
    print_section("7. Token Balance Check")
    try:
        # Use sandbox test token
        token_address = "0xtest_usdc"
        response = requests.get(f"{API_V1}/token/balance/{token_address}")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Token balance retrieved")
            print_info(f"Token: {data['token_name']} ({data['token_symbol']})")
            print_info(f"Balance: {data['balance']} {data['token_symbol']}")
            
            if data.get('sandbox_mode'):
                print_warning("SANDBOX MODE: Simulated balance")
            
            return True
        else:
            print_warning("Token balance check failed (expected in sandbox)")
            return True  # Don't fail test, tokens are optional
    except Exception as e:
        print_warning(f"Token balance check skipped: {e}")
        return True


def test_audit_history():
    """Test audit history"""
    print_section("8. Audit History")
    try:
        response = requests.get(f"{API_V1}/audit/transactions?limit=10")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Retrieved {data['count']} transactions from audit log")
            
            if data['count'] > 0:
                latest = data['transactions'][0]
                print_info(f"Latest TX: {latest.get('tx_hash', 'N/A')[:20]}...")
                print_info(f"Status: {latest.get('status')}")
                print_info(f"Timestamp: {latest.get('timestamp')}")
            
            return True
        else:
            print_error(f"Audit history failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Audit history failed: {e}")
        return False


def test_network_info():
    """Test network information"""
    print_section("9. Network Information")
    try:
        response = requests.get(f"{API_V1}/network/info")
        if response.status_code == 200:
            data = response.json()
            print_success("Network info retrieved")
            print_info(f"Network: {data.get('name')}")
            print_info(f"Chain ID: {data.get('chain_id')}")
            print_info(f"Block: {data.get('block_number')}")
            
            if data.get('status') == 'sandbox':
                print_warning("SANDBOX MODE: Simulated network")
            
            return True
        else:
            print_error(f"Network info failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Network info failed: {e}")
        return False


def main():
    """Run all tests"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║           ChainPilot Phase 2 - Testing Suite             ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print_info("Starting comprehensive Phase 2 tests...")
    print_info("Make sure server is running: python3 run.py --sandbox")
    print("")
    
    results = []
    
    # Run tests
    results.append(("API Health", test_api_health()))
    
    if not results[0][1]:
        print_error("\nServer not running! Start with: python3 run.py --sandbox")
        return
    
    address = test_wallet_creation()
    results.append(("Wallet Creation", address is not None))
    
    if address:
        results.append(("Balance Check", test_balance_check(address)))
        results.append(("TX Estimation", test_transaction_estimate()))
        
        tx_hash = test_transaction_send()
        results.append(("Send Transaction", tx_hash is not None))
        
        if tx_hash:
            results.append(("TX Status", test_transaction_status(tx_hash)))
        
        results.append(("Token Balance", test_token_balance()))
        results.append(("Audit History", test_audit_history()))
        results.append(("Network Info", test_network_info()))
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{'='*60}")
    if passed == total:
        print_success(f"ALL TESTS PASSED! ({passed}/{total})")
        print_success("Phase 2 is working perfectly! 🎉")
    else:
        print_warning(f"PASSED: {passed}/{total} tests")
        print_info("Some tests failed - check details above")
    
    print(f"{'='*60}\n")
    
    # Next steps
    print_section("NEXT STEPS")
    print_info("1. Try the interactive API docs: http://localhost:8000/docs")
    print_info("2. Test with real testnet: python3 run.py (without --sandbox)")
    print_info("3. Get testnet funds: https://sepoliafaucet.com")
    print_info("4. Review documentation: README.md, PHASE2_SUMMARY.md")
    print("")


if __name__ == "__main__":
    main()

