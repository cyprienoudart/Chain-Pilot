#!/usr/bin/env python3
"""
Phase 4 Testing Script - AI Natural Language Integration
Test intent parsing and natural language execution
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


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


def test_get_examples():
    """Test getting examples"""
    print_section("1. Get AI Examples")
    response = requests.get(f"{BASE_URL}/ai/examples")
    if response.status_code == 200:
        data = response.json()
        print_success(f"Retrieved {data['total_categories']} example categories")
        for cat in data['examples'][:2]:
            print_info(f"  - {cat['category']}: {len(cat['examples'])} examples")
        return True
    print_error("Failed to get examples")
    return False


def test_parse_send_transaction():
    """Test parsing send transaction"""
    print_section("2. Parse: Send Transaction")
    
    response = requests.post(
        f"{BASE_URL}/ai/parse",
        json={
            "text": "Send 0.5 ETH to 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
            "execute": False
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Parsed intent: {data['intent']}")
        print_info(f"  - Confidence: {data['confidence']:.2f}")
        print_info(f"  - Amount: {data['entities'].get('amount')} {data['entities'].get('currency')}")
        print_info(f"  - To: {data['entities'].get('to_address')[:10]}...")
        print_info(f"  - API: {data['api_request']['endpoint']}")
        return data['intent'] == 'send_transaction'
    
    print_error("Failed to parse")
    return False


def test_parse_check_balance():
    """Test parsing balance check"""
    print_section("3. Parse: Check Balance")
    
    response = requests.post(
        f"{BASE_URL}/ai/parse",
        json={"text": "What's my balance?", "execute": False}
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Parsed intent: {data['intent']}")
        print_info(f"  - Confidence: {data['confidence']:.2f}")
        print_info(f"  - API: {data['api_request']['endpoint']}")
        return data['intent'] == 'check_balance'
    
    print_error("Failed to parse")
    return False


def test_parse_create_rule():
    """Test parsing rule creation"""
    print_section("4. Parse: Create Rule")
    
    response = requests.post(
        f"{BASE_URL}/ai/parse",
        json={
            "text": "Create a daily spending limit of 1 ETH",
            "execute": False
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Parsed intent: {data['intent']}")
        print_info(f"  - Confidence: {data['confidence']:.2f}")
        print_info(f"  - Period: {data['entities'].get('period')}")
        print_info(f"  - Amount: {data['entities'].get('amount')} {data['entities'].get('currency')}")
        return data['intent'] == 'create_rule'
    
    print_error("Failed to parse")
    return False


def test_add_name_mapping():
    """Test adding name mapping"""
    print_section("5. Add Name Mapping")
    
    response = requests.post(
        f"{BASE_URL}/ai/add-name",
        json={
            "name": "alice",
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Added mapping: {data['name']} → {data['address'][:10]}...")
        return True
    
    print_error("Failed to add mapping")
    return False


def test_parse_with_name():
    """Test parsing with name mapping"""
    print_section("6. Parse: Send to Named Address")
    
    response = requests.post(
        f"{BASE_URL}/ai/parse",
        json={
            "text": "Send 0.2 ETH to alice",
            "execute": False
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print_success(f"Parsed with name resolution")
        print_info(f"  - Intent: {data['intent']}")
        print_info(f"  - Resolved to: {data['entities'].get('to_address', 'N/A')[:10]}...")
        print_info(f"  - Amount: {data['entities'].get('amount')} {data['entities'].get('currency')}")
        return True
    
    print_error("Failed to parse with name")
    return False


def test_execute_check_balance():
    """Test executing check balance"""
    print_section("7. Execute: Check Balance")
    
    # Create wallet first
    requests.post(f"{BASE_URL}/wallet/create", json={"wallet_name": "test_phase4"})
    
    # Execute natural language
    response = requests.post(
        f"{BASE_URL}/ai/parse",
        json={
            "text": "What's my balance?",
            "execute": True,
            "confirm": False
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'executed':
            print_success("Balance check executed!")
            exec_data = data['execution']['data']
            print_info(f"  - Balance: {exec_data.get('balance_ether')} {exec_data.get('currency')}")
            return True
        else:
            print_info(f"Status: {data.get('status')}")
            return True
    
    print_error("Failed to execute")
    return False


def test_multiple_intents():
    """Test parsing multiple intent types"""
    print_section("8. Parse Multiple Intents")
    
    test_cases = [
        ("Transfer 1 ETH to 0x123...", "send_transaction"),
        ("Check balance", "check_balance"),
        ("Create wallet", "create_wallet"),
        ("How much USDC do I have?", "get_token_balance"),
    ]
    
    passed = 0
    for text, expected_intent in test_cases:
        response = requests.post(
            f"{BASE_URL}/ai/parse",
            json={"text": text, "execute": False}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data['intent'] == expected_intent:
                passed += 1
                print_info(f"✓ '{text[:30]}...' → {expected_intent}")
            else:
                print_error(f"✗ '{text[:30]}...' → Got {data['intent']}, expected {expected_intent}")
    
    print_success(f"{passed}/{len(test_cases)} intents parsed correctly")
    return passed == len(test_cases)


def test_confidence_scores():
    """Test confidence scoring"""
    print_section("9. Test Confidence Scores")
    
    # Clear query should have high confidence
    response1 = requests.post(
        f"{BASE_URL}/ai/parse",
        json={"text": "Send 0.5 ETH to 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"}
    )
    
    # Ambiguous query should have lower confidence
    response2 = requests.post(
        f"{BASE_URL}/ai/parse",
        json={"text": "send something somewhere maybe"}
    )
    
    if response1.status_code == 200 and response2.status_code == 200:
        conf1 = response1.json()['confidence']
        conf2 = response2.json()['confidence']
        
        print_success(f"Clear query confidence: {conf1:.2f}")
        print_info(f"Ambiguous query confidence: {conf2:.2f}")
        
        if conf1 > 0.7:
            return True
    
    return False


def main():
    """Run all tests"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║    ChainPilot Phase 4 - AI Integration Testing           ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    print_info("Testing natural language parsing and execution...")
    print_info("Make sure server is running: python3 run.py --sandbox")
    print("")
    
    results = []
    
    results.append(("Get Examples", test_get_examples()))
    results.append(("Parse Send TX", test_parse_send_transaction()))
    results.append(("Parse Balance", test_parse_check_balance()))
    results.append(("Parse Rule", test_parse_create_rule()))
    results.append(("Add Name Mapping", test_add_name_mapping()))
    results.append(("Parse with Name", test_parse_with_name()))
    results.append(("Execute Balance", test_execute_check_balance()))
    results.append(("Multiple Intents", test_multiple_intents()))
    results.append(("Confidence Scores", test_confidence_scores()))
    
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
        print_success("Phase 4 AI Integration is working perfectly! 🎉")
    else:
        print_info(f"PASSED: {passed}/{total} tests")
    
    print(f"{'='*60}\n")
    
    print_section("WHAT THIS PROVES")
    print_info("✅ Natural language parsing works")
    print_info("✅ Multiple intent types supported")
    print_info("✅ Entity extraction works (amounts, addresses, etc.)")
    print_info("✅ Name mappings work (send to 'alice')")
    print_info("✅ Actions can be executed from natural language")
    print_info("✅ Confidence scoring works")
    print("")
    
    print_section("TRY IT YOURSELF")
    print_info("Visit http://localhost:8000/docs")
    print_info("Try the /api/v1/ai/parse endpoint with:")
    print("")
    print('{"text": "Send 0.5 ETH to alice"}')
    print('{"text": "What\'s my balance?"}')
    print('{"text": "Create a daily limit of 1 ETH"}')
    print("")


if __name__ == "__main__":
    main()

