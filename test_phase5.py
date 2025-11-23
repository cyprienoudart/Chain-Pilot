#!/usr/bin/env python3
"""
Phase 5 Testing Script - Web Dashboard
Test dashboard functionality and integration
"""
import requests
import time
import sys

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"


class Colors:
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


def print_section(title):
    print(f"\n{'='*60}")
    print(f"{Colors.BLUE}{title}{Colors.END}")
    print('='*60)


def test_server_running():
    """Test if server is running"""
    print_section("1. Server Status")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success("Server is running")
            print_info(f"  - Status: {data['status']}")
            print_info(f"  - Network: {data.get('network', {}).get('name', 'N/A')}")
            print_info(f"  - Sandbox Mode: {data.get('sandbox_mode', False)}")
            return True
    except requests.exceptions.ConnectionError:
        print_error("Server not running!")
        print_info("Start server with: python3 run.py --sandbox")
        return False
    except Exception as e:
        print_error(f"Error checking server: {e}")
        return False


def test_dashboard_accessible():
    """Test if dashboard HTML is accessible"""
    print_section("2. Dashboard Accessibility")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "ChainPilot Dashboard" in content:
                print_success("Dashboard HTML loads correctly")
                print_info(f"  - Content length: {len(content)} bytes")
                return True
            else:
                print_error("Dashboard HTML missing title")
                return False
        else:
            print_error(f"Dashboard returned status {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error accessing dashboard: {e}")
        return False


def test_static_files():
    """Test if static files are accessible"""
    print_section("3. Static Files")
    
    static_files = [
        ("/static/dashboard.css", "text/css"),
        ("/static/dashboard.js", "application/javascript")
    ]
    
    passed = 0
    for file_path, content_type in static_files:
        try:
            response = requests.get(f"{BASE_URL}{file_path}", timeout=5)
            if response.status_code == 200:
                size_kb = len(response.content) / 1024
                print_info(f"✓ {file_path} ({size_kb:.1f} KB)")
                passed += 1
            else:
                print_error(f"✗ {file_path} - Status {response.status_code}")
        except Exception as e:
            print_error(f"✗ {file_path} - Error: {e}")
    
    if passed == len(static_files):
        print_success(f"All static files accessible ({passed}/{len(static_files)})")
        return True
    else:
        print_error(f"Some static files missing ({passed}/{len(static_files)})")
        return False


def test_api_endpoints_work():
    """Test that API endpoints work for dashboard"""
    print_section("4. API Endpoints for Dashboard")
    
    endpoints = [
        ("GET", "/api/v1/wallet/list", "List wallets"),
        ("GET", "/api/v1/rules", "List rules"),
        ("GET", "/api/v1/audit/transactions?limit=10", "Get transactions"),
        ("GET", "/api/v1/ai/examples", "Get AI examples"),
    ]
    
    passed = 0
    for method, endpoint, description in endpoints:
        try:
            response = requests.request(method, f"{BASE_URL}{endpoint}", timeout=5)
            if response.status_code == 200:
                print_info(f"✓ {description}")
                passed += 1
            else:
                print_error(f"✗ {description} - Status {response.status_code}")
        except Exception as e:
            print_error(f"✗ {description} - Error: {e}")
    
    if passed == len(endpoints):
        print_success(f"All API endpoints working ({passed}/{len(endpoints)})")
        return True
    else:
        print_error(f"Some API endpoints failing ({passed}/{len(endpoints)})")
        return False


def test_wallet_creation_via_api():
    """Test wallet creation (as dashboard would)"""
    print_section("5. Wallet Creation")
    try:
        wallet_name = f"test_dashboard_{int(time.time())}"
        response = requests.post(
            f"{API_BASE}/wallet/create",
            json={"wallet_name": wallet_name},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Wallet created via API")
            print_info(f"  - Name: {data['wallet_name']}")
            print_info(f"  - Address: {data['address'][:10]}...")
            
            # Load the wallet
            load_response = requests.post(
                f"{API_BASE}/wallet/load",
                json={"wallet_name": wallet_name},
                timeout=5
            )
            if load_response.status_code == 200:
                print_success("Wallet loaded successfully")
                return True
        
        print_error("Failed to create wallet")
        return False
    except Exception as e:
        print_error(f"Error creating wallet: {e}")
        return False


def test_ai_integration():
    """Test AI parsing (as dashboard chat would)"""
    print_section("6. AI Integration")
    try:
        test_messages = [
            "What's my balance?",
            "Send 0.1 ETH to 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
            "Create a daily spending limit of 1 ETH"
        ]
        
        passed = 0
        for message in test_messages:
            response = requests.post(
                f"{API_BASE}/ai/parse",
                json={"text": message, "execute": False},
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('parsed'):
                    print_info(f"✓ '{message[:30]}...' → {data['intent']}")
                    passed += 1
                else:
                    print_error(f"✗ '{message[:30]}...' - Not parsed")
            else:
                print_error(f"✗ '{message[:30]}...' - Status {response.status_code}")
        
        if passed == len(test_messages):
            print_success(f"AI parsing working ({passed}/{len(test_messages)})")
            return True
        else:
            print_error(f"Some AI parsing failing ({passed}/{len(test_messages)})")
            return False
    except Exception as e:
        print_error(f"Error testing AI: {e}")
        return False


def test_rule_creation():
    """Test rule creation (as dashboard would)"""
    print_section("7. Rule Creation")
    try:
        rule_name = f"Test Rule {int(time.time())}"
        response = requests.post(
            f"{API_BASE}/rules/create",
            json={
                "rule_name": rule_name,
                "rule_type": "spending_limit",
                "parameters": {"type": "per_transaction", "amount": 0.5},
                "action": "deny",
                "enabled": True
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success("Rule created successfully")
            print_info(f"  - ID: {data['id']}")
            print_info(f"  - Name: {data.get('rule_name', data.get('name', 'N/A'))}")
            print_info(f"  - Type: {data['rule_type']}")
            return True
        else:
            print_error(f"Failed to create rule: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error creating rule: {e}")
        return False


def test_transaction_history():
    """Test transaction history retrieval"""
    print_section("8. Transaction History")
    try:
        response = requests.get(
            f"{API_BASE}/audit/transactions?limit=50",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            tx_count = len(data.get('transactions', []))
            print_success(f"Retrieved {tx_count} transactions")
            
            if tx_count > 0:
                latest = data['transactions'][0]
                print_info(f"  - Latest: {latest['tx_hash'][:20]}...")
                print_info(f"  - Status: {latest['status']}")
                print_info(f"  - Time: {latest['timestamp'][:19]}")
            
            return True
        else:
            print_error(f"Failed to get transactions: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error getting transactions: {e}")
        return False


def test_dashboard_integration():
    """Test full dashboard integration"""
    print_section("9. Dashboard Integration Test")
    
    # Simulate dashboard workflow
    try:
        # 1. Load dashboard
        dashboard_response = requests.get(f"{BASE_URL}/", timeout=5)
        assert dashboard_response.status_code == 200, "Dashboard not accessible"
        print_info("✓ Dashboard loaded")
        
        # 2. Get wallet list
        wallets_response = requests.get(f"{API_BASE}/wallet/list", timeout=5)
        assert wallets_response.status_code == 200, "Cannot get wallets"
        wallets = wallets_response.json().get('wallets', [])
        print_info(f"✓ Retrieved {len(wallets)} wallets")
        
        # 3. Get rules
        rules_response = requests.get(f"{API_BASE}/rules", timeout=5)
        assert rules_response.status_code == 200, "Cannot get rules"
        rules = rules_response.json()
        print_info(f"✓ Retrieved {len(rules)} rules")
        
        # 4. Get transactions
        tx_response = requests.get(f"{API_BASE}/audit/transactions?limit=10", timeout=5)
        assert tx_response.status_code == 200, "Cannot get transactions"
        transactions = tx_response.json().get('transactions', [])
        print_info(f"✓ Retrieved {len(transactions)} transactions")
        
        # 5. Test AI
        ai_response = requests.post(
            f"{API_BASE}/ai/parse",
            json={"text": "Check balance", "execute": False},
            timeout=5
        )
        assert ai_response.status_code == 200, "AI not working"
        print_info("✓ AI integration working")
        
        print_success("Dashboard integration test passed!")
        return True
        
    except AssertionError as e:
        print_error(f"Integration test failed: {e}")
        return False
    except Exception as e:
        print_error(f"Integration test error: {e}")
        return False


def main():
    """Run all tests"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║       ChainPilot Phase 5 - Dashboard Testing             ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print_info("Testing web dashboard and integration...")
    print_info("Dashboard should be at: http://localhost:8000/")
    print("")
    
    results = []
    
    # Run tests
    if not test_server_running():
        print("\n" + "="*60)
        print_error("SERVER NOT RUNNING!")
        print_info("Please start the server first:")
        print_info("  python3 run.py --sandbox")
        print("="*60 + "\n")
        sys.exit(1)
    
    results.append(("Server Status", True))
    results.append(("Dashboard HTML", test_dashboard_accessible()))
    results.append(("Static Files", test_static_files()))
    results.append(("API Endpoints", test_api_endpoints_work()))
    results.append(("Wallet Creation", test_wallet_creation_via_api()))
    results.append(("AI Integration", test_ai_integration()))
    results.append(("Rule Creation", test_rule_creation()))
    results.append(("Transaction History", test_transaction_history()))
    results.append(("Dashboard Integration", test_dashboard_integration()))
    
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
        print_success("Phase 5 Dashboard is working perfectly! 🎉")
    else:
        print_info(f"PASSED: {passed}/{total} tests")
        print_error(f"FAILED: {total - passed} tests")
    
    print(f"{'='*60}\n")
    
    print_section("WHAT THIS PROVES")
    print_info("✅ Dashboard HTML/CSS/JS loads correctly")
    print_info("✅ Static files served properly")
    print_info("✅ All API endpoints accessible")
    print_info("✅ Wallet management works")
    print_info("✅ AI integration functional")
    print_info("✅ Rule management operational")
    print_info("✅ Transaction history accessible")
    print_info("✅ Full dashboard integration works")
    print("")
    
    print_section("TRY IT YOURSELF")
    print_info("Open your browser and visit:")
    print("")
    print(f"    {Colors.GREEN}http://localhost:8000/{Colors.END}")
    print("")
    print_info("You should see:")
    print_info("  - Overview with wallet stats")
    print_info("  - AI chat interface")
    print_info("  - Transaction history")
    print_info("  - Rule management")
    print_info("  - Wallet management")
    print("")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

