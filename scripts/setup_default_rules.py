#!/usr/bin/env python3
"""
Setup Default Rules for ChainPilot
Cleans up duplicate rules and ensures sensible defaults exist
"""
import requests
import time

BASE_URL = "http://localhost:8000/api/v1"

# Color codes
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

def get_all_rules():
    """Get all rules from the server"""
    try:
        response = requests.get(f"{BASE_URL}/rules")
        if response.status_code == 200:
            return response.json()["rules"]
        return []
    except Exception as e:
        print_error(f"Failed to get rules: {e}")
        return []

def delete_rule(rule_id):
    """Delete a rule by ID"""
    try:
        response = requests.delete(f"{BASE_URL}/rules/{rule_id}")
        return response.status_code == 200
    except Exception as e:
        print_error(f"Failed to delete rule {rule_id}: {e}")
        return False

def create_rule(rule_data):
    """Create a new rule"""
    try:
        response = requests.post(f"{BASE_URL}/rules/create", json=rule_data)
        if response.status_code == 200:
            return response.json()["rule_id"]
        else:
            print_error(f"Failed to create rule: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print_error(f"Failed to create rule: {e}")
        return None

def clean_duplicate_rules():
    """Remove duplicate test rules"""
    print_section("Cleaning Duplicate Rules")
    
    rules = get_all_rules()
    print_info(f"Found {len(rules)} total rules")
    
    # Group rules by name and type
    rule_groups = {}
    for rule in rules:
        key = (rule['rule_name'], rule['rule_type'])
        if key not in rule_groups:
            rule_groups[key] = []
        rule_groups[key].append(rule)
    
    # Keep only the first rule in each group, delete duplicates
    deleted_count = 0
    for key, group in rule_groups.items():
        if len(group) > 1:
            print_info(f"Found {len(group)} duplicates of '{key[0]}'")
            # Keep the first one, delete the rest
            for rule in group[1:]:
                if delete_rule(rule['rule_id']):
                    print_success(f"Deleted duplicate rule ID {rule['rule_id']}")
                    deleted_count += 1
    
    if deleted_count == 0:
        print_success("No duplicate rules found")
    else:
        print_success(f"Removed {deleted_count} duplicate rules")
    
    return deleted_count

def setup_default_rules():
    """Ensure default rules exist"""
    print_section("Setting Up Default Rules")
    
    # Get current rules
    current_rules = get_all_rules()
    existing_names = {rule['rule_name'] for rule in current_rules}
    
    # Define default rules
    default_rules = [
        {
            "rule_type": "spending_limit",
            "rule_name": "Daily Spending Limit",
            "parameters": {"type": "daily", "amount": 1.0},
            "action": "deny",
            "enabled": True,
            "priority": 5
        },
        {
            "rule_type": "amount_threshold",
            "rule_name": "Large Transaction Approval",
            "parameters": {"threshold": 0.5},
            "action": "require_approval",
            "enabled": True,
            "priority": 10
        },
        {
            "rule_type": "spending_limit",
            "rule_name": "Per-Transaction Limit",
            "parameters": {"type": "per_transaction", "amount": 0.1},
            "action": "deny",
            "enabled": False,
            "priority": 3
        }
    ]
    
    created_count = 0
    for rule_data in default_rules:
        if rule_data['rule_name'] not in existing_names:
            print_info(f"Creating rule: {rule_data['rule_name']}")
            rule_id = create_rule(rule_data)
            if rule_id:
                print_success(f"Created rule '{rule_data['rule_name']}' (ID: {rule_id})")
                created_count += 1
        else:
            print_info(f"Rule already exists: {rule_data['rule_name']}")
    
    if created_count == 0:
        print_success("All default rules already exist")
    else:
        print_success(f"Created {created_count} new default rules")
    
    return created_count

def display_current_rules():
    """Display current rules"""
    print_section("Current Rules")
    
    rules = get_all_rules()
    
    if not rules:
        print_info("No rules configured")
        return
    
    print_info(f"Total rules: {len(rules)}")
    print()
    
    for rule in rules:
        status = "🟢 ENABLED" if rule['enabled'] else "🔴 DISABLED"
        print(f"  {status} [{rule['rule_id']}] {rule['rule_name']}")
        print(f"       Type: {rule['rule_type']}")
        print(f"       Action: {rule['action']}")
        print(f"       Priority: {rule['priority']}")
        print(f"       Parameters: {rule['parameters']}")
        print()

def main():
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}ChainPilot - Setup Default Rules{RESET}")
    print(f"{BLUE}{'='*70}{RESET}")
    
    # Check server health
    print_info("Checking server...")
    try:
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print_success("Server is running")
        else:
            print_error("Server is not healthy")
            return
    except Exception as e:
        print_error(f"Cannot connect to server: {e}")
        print_info("Make sure server is running: python3 run.py --sandbox")
        return
    
    # Clean duplicates
    deleted = clean_duplicate_rules()
    
    # Setup defaults
    created = setup_default_rules()
    
    # Display current state
    display_current_rules()
    
    print_section("Summary")
    print_success(f"Deleted {deleted} duplicate rules")
    print_success(f"Created {created} new default rules")
    print_success("Rules setup complete!")
    print_info("Open dashboard at: http://localhost:8000/")
    print()

if __name__ == "__main__":
    main()

