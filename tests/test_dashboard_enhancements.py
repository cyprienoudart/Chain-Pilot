#!/usr/bin/env python3
"""
Test Dashboard Enhancements
Tests new rule management and wallet visualization features
"""
import requests
import time
import json

BASE_URL = "http://localhost:8000/api/v1"
DASHBOARD_URL = "http://localhost:8000"

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_section(title):
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")

def print_success(message):
    print(f"{GREEN}✅ {message}{RESET}")

def print_error(message):
    print(f"{RED}❌ {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ️  {message}{RESET}")

def test_rule_management():
    """Test enhanced rule management features"""
    print_section("Testing Rule Management")
    
    # 1. Create a test rule
    print_info("Creating test rule...")
    rule_data = {
        "rule_type": "spending_limit",
        "rule_name": "Test Daily Limit",
        "parameters": {"type": "daily", "amount": 0.5},
        "action": "deny",
        "enabled": True,
        "priority": 1
    }
    
    response = requests.post(f"{BASE_URL}/rules/create", json=rule_data)
    if response.status_code == 200:
        rule_id = response.json()["rule_id"]
        print_success(f"Rule created with ID: {rule_id}")
    else:
        print_error(f"Failed to create rule: {response.status_code} - {response.text}")
        return False
    
    # 2. List rules
    print_info("Listing rules...")
    response = requests.get(f"{BASE_URL}/rules")
    if response.status_code == 200:
        rules = response.json()["rules"]
        print_success(f"Found {len(rules)} rule(s)")
        for rule in rules:
            print_info(f"  - {rule['rule_name']} ({rule['rule_type']}) - {'Enabled' if rule['enabled'] else 'Disabled'}")
    else:
        print_error(f"Failed to list rules: {response.status_code}")
        return False
    
    # 3. Update rule (change parameters)
    print_info("Updating rule parameters...")
    update_data = {
        "parameters": {"type": "daily", "amount": 1.0},
        "priority": 2
    }
    response = requests.put(f"{BASE_URL}/rules/{rule_id}", json=update_data)
    if response.status_code == 200:
        print_success("Rule parameters updated successfully")
    else:
        print_error(f"Failed to update rule: {response.status_code} - {response.text}")
        return False
    
    # 4. Toggle rule (disable)
    print_info("Disabling rule...")
    toggle_data = {"enabled": False}
    response = requests.put(f"{BASE_URL}/rules/{rule_id}", json=toggle_data)
    if response.status_code == 200:
        print_success("Rule disabled successfully")
    else:
        print_error(f"Failed to disable rule: {response.status_code}")
        return False
    
    # 5. Toggle rule (enable)
    print_info("Re-enabling rule...")
    toggle_data = {"enabled": True}
    response = requests.put(f"{BASE_URL}/rules/{rule_id}", json=toggle_data)
    if response.status_code == 200:
        print_success("Rule enabled successfully")
    else:
        print_error(f"Failed to enable rule: {response.status_code}")
        return False
    
    # 6. Verify rule was updated
    print_info("Verifying rule changes...")
    response = requests.get(f"{BASE_URL}/rules")
    if response.status_code == 200:
        rules = response.json()["rules"]
        updated_rule = next((r for r in rules if r["rule_id"] == rule_id), None)
        if updated_rule:
            if updated_rule["parameters"]["amount"] == 1.0 and updated_rule["priority"] == 2:
                print_success("Rule changes verified successfully")
            else:
                print_error(f"Rule changes not applied correctly: {updated_rule}")
                return False
        else:
            print_error("Rule not found after update")
            return False
    
    # 7. Delete rule
    print_info("Deleting test rule...")
    response = requests.delete(f"{BASE_URL}/rules/{rule_id}")
    if response.status_code == 200:
        print_success("Rule deleted successfully")
    else:
        print_error(f"Failed to delete rule: {response.status_code}")
        return False
    
    return True

def test_wallet_management():
    """Test enhanced wallet visualization and switching"""
    print_section("Testing Wallet Management")
    
    # 1. Create test wallets
    test_wallet_names = [f"test_enh_wallet_{int(time.time())}_{i}" for i in range(2)]
    created_wallet_addresses = []
    
    for wallet_name in test_wallet_names:
        print_info(f"Creating wallet: {wallet_name}...")
        response = requests.post(f"{BASE_URL}/wallet/create", json={"wallet_name": wallet_name})
        if response.status_code == 200:
            wallet_data = response.json()
            created_wallet_addresses.append({"name": wallet_name, "address": wallet_data['address']})
            print_success(f"Wallet created: {wallet_data['address'][:20]}...")
        else:
            print_error(f"Failed to create wallet: {response.status_code}")
    
    if len(created_wallet_addresses) < 2:
        print_error("Failed to create enough test wallets")
        return False
    
    # 2. List wallets
    print_info("Listing wallets...")
    response = requests.get(f"{BASE_URL}/wallet/list")
    if response.status_code == 200:
        wallets_data = response.json()
        
        # Handle different response formats
        if isinstance(wallets_data, list):
            wallet_list = wallets_data
        elif isinstance(wallets_data, dict) and 'wallets' in wallets_data:
            wallet_list = wallets_data['wallets']
        else:
            wallet_list = []
        
        print_success(f"Found {len(wallet_list)} wallet(s)")
        
        # Display wallet info (show first 5)
        for wallet in wallet_list[:5]:
            if isinstance(wallet, dict):
                wallet_info = f"  - {wallet.get('name', 'Unknown')}: {wallet.get('address', '')[:20]}... ({wallet.get('network', 'Unknown')})"
                print_info(wallet_info)
            else:
                print_info(f"  - {wallet}")
    else:
        print_error(f"Failed to list wallets: {response.status_code}")
        return False
    
    # 3. Switch between wallets
    for wallet in created_wallet_addresses:
        print_info(f"Switching to wallet: {wallet['name']}...")
        response = requests.post(f"{BASE_URL}/wallet/load", json={"wallet_name": wallet['name']})
        if response.status_code == 200:
            print_success(f"Switched to {wallet['name']}")
            
            # Verify balance query works
            balance_response = requests.get(f"{BASE_URL}/wallet/balance")
            if balance_response.status_code == 200:
                balance_data = balance_response.json()
                balance = balance_data.get('balance_ether', balance_data.get('balance_eth', 0))
                print_info(f"  Balance: {balance} ETH")
                print_info(f"  Address: {balance_data['address'][:20]}...")
                
                # Verify correct wallet is loaded
                if balance_data['address'].lower() != wallet['address'].lower():
                    print_error(f"Wrong wallet loaded! Expected {wallet['address']}, got {balance_data['address']}")
                    return False
            else:
                print_error(f"Failed to query balance after switching: {balance_response.status_code}")
                return False
        else:
            print_error(f"Failed to switch wallet: {response.status_code}")
            return False
    
    # 4. Test rule templates (for creating rules easily)
    print_info("Testing rule templates...")
    response = requests.get(f"{BASE_URL}/rules/templates")
    if response.status_code == 200:
        templates = response.json()["templates"]
        print_success(f"Found {len(templates)} rule template(s)")
        for template in templates[:3]:  # Show first 3
            print_info(f"  - {template['name']}: {template['description']}")
    else:
        print_error(f"Failed to get rule templates: {response.status_code}")
    
    return True

def test_dashboard_accessibility():
    """Test that dashboard pages load correctly"""
    print_section("Testing Dashboard Accessibility")
    
    # 1. Check main dashboard
    print_info("Checking main dashboard...")
    response = requests.get(DASHBOARD_URL)
    if response.status_code == 200 and "ChainPilot Dashboard" in response.text:
        print_success("Main dashboard accessible")
    else:
        print_error(f"Dashboard not accessible: {response.status_code}")
        return False
    
    # 2. Check CSS
    print_info("Checking dashboard CSS...")
    response = requests.get(f"{DASHBOARD_URL}/static/dashboard.css")
    if response.status_code == 200 and "rule-card" in response.text and "wallet-card" in response.text:
        print_success("Dashboard CSS includes new styles")
    else:
        print_error("Dashboard CSS missing new styles")
        return False
    
    # 3. Check JavaScript
    print_info("Checking dashboard JavaScript...")
    response = requests.get(f"{DASHBOARD_URL}/static/dashboard.js")
    if response.status_code == 200:
        js_content = response.text
        required_functions = [
            "loadRules",
            "toggleRule",
            "editRule",
            "deleteRule",
            "loadWalletsEnhanced",
            "switchWallet",
            "showNotification"
        ]
        
        missing_functions = [fn for fn in required_functions if fn not in js_content]
        if not missing_functions:
            print_success("All required JavaScript functions present")
        else:
            print_error(f"Missing JavaScript functions: {', '.join(missing_functions)}")
            return False
    else:
        print_error("Dashboard JavaScript not accessible")
        return False
    
    return True

def main():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}ChainPilot Dashboard Enhancements Test Suite{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    # Check server health
    print_info("Checking server health...")
    try:
        response = requests.get(f"{DASHBOARD_URL}/health")
        if response.status_code == 200:
            health = response.json()
            print_success(f"Server is healthy (Sandbox: {health.get('sandbox_mode', False)})")
        else:
            print_error("Server is not healthy")
            return
    except Exception as e:
        print_error(f"Cannot connect to server: {e}")
        print_info("Make sure server is running: python3 run.py --sandbox")
        return
    
    # Run tests
    results = {
        "Rule Management": test_rule_management(),
        "Wallet Management": test_wallet_management(),
        "Dashboard Accessibility": test_dashboard_accessibility()
    }
    
    # Summary
    print_section("Test Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        if result:
            print_success(f"{test_name}")
        else:
            print_error(f"{test_name}")
    
    print(f"\n{BLUE}Results: {passed}/{total} test categories passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}{'='*70}{RESET}")
        print(f"{GREEN}🎉 ALL TESTS PASSED! Dashboard enhancements are working!{RESET}")
        print(f"{GREEN}{'='*70}{RESET}")
        print(f"\n{BLUE}You can now:{RESET}")
        print(f"{BLUE}  1. Modify rules directly in the dashboard{RESET}")
        print(f"{BLUE}  2. Toggle rules on/off with a switch{RESET}")
        print(f"{BLUE}  3. Edit rule parameters{RESET}")
        print(f"{BLUE}  4. View detailed rule descriptions{RESET}")
        print(f"{BLUE}  5. Switch between wallets easily{RESET}")
        print(f"{BLUE}  6. See visual wallet information{RESET}")
        print(f"\n{BLUE}Open your browser to: {DASHBOARD_URL}{RESET}\n")
    else:
        print(f"\n{YELLOW}{'='*70}{RESET}")
        print(f"{YELLOW}⚠️  Some tests failed. Check errors above.{RESET}")
        print(f"{YELLOW}{'='*70}{RESET}\n")

if __name__ == "__main__":
    main()

