"""
ChainPilot API Client Example
Demonstrates how to interact with the ChainPilot API
"""
import requests
import json
from typing import Dict, Any

# API Base URL
BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"


class ChainPilotClient:
    """Simple client for interacting with ChainPilot API"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.api_v1 = f"{base_url}/api/v1"
    
    def check_health(self) -> Dict[str, Any]:
        """Check API health and Web3 connection status"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get blockchain network information"""
        response = requests.get(f"{self.api_v1}/network/info")
        response.raise_for_status()
        return response.json()
    
    def create_wallet(self, wallet_name: str = "default") -> Dict[str, Any]:
        """Create a new wallet"""
        response = requests.post(
            f"{self.api_v1}/wallet/create",
            json={"wallet_name": wallet_name}
        )
        response.raise_for_status()
        return response.json()
    
    def load_wallet(self, wallet_name: str = "default") -> Dict[str, Any]:
        """Load an existing wallet"""
        response = requests.post(
            f"{self.api_v1}/wallet/load",
            json={"wallet_name": wallet_name}
        )
        response.raise_for_status()
        return response.json()
    
    def list_wallets(self) -> Dict[str, Any]:
        """List all available wallets"""
        response = requests.get(f"{self.api_v1}/wallet/list")
        response.raise_for_status()
        return response.json()
    
    def get_current_wallet(self) -> Dict[str, Any]:
        """Get current wallet address"""
        response = requests.get(f"{self.api_v1}/wallet/current")
        response.raise_for_status()
        return response.json()
    
    def get_balance(self, address: str = None) -> Dict[str, Any]:
        """Get wallet balance"""
        params = {"address": address} if address else {}
        response = requests.get(f"{self.api_v1}/wallet/balance", params=params)
        response.raise_for_status()
        return response.json()
    
    def get_transaction_history(self, address: str = None, limit: int = 10) -> Dict[str, Any]:
        """Get transaction history"""
        params = {}
        if address:
            params["address"] = address
        if limit:
            params["limit"] = limit
        
        response = requests.get(f"{self.api_v1}/wallet/history", params=params)
        response.raise_for_status()
        return response.json()


def main():
    """Demo: Complete workflow"""
    print("=" * 60)
    print("ChainPilot API Client Demo")
    print("=" * 60)
    print()
    
    # Initialize client
    client = ChainPilotClient()
    
    # 1. Check health
    print("1️⃣  Checking API health...")
    try:
        health = client.check_health()
        print(f"   Status: {health['status']}")
        print(f"   Web3 Connected: {health['web3_connected']}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Make sure the API is running: ./start_api.sh")
        return
    
    # 2. Get network info
    print("2️⃣  Getting network information...")
    try:
        network = client.get_network_info()
        print(f"   Network: {network['name']}")
        print(f"   Chain ID: {network['chain_id']}")
        print(f"   Currency: {network['currency']}")
        print(f"   Block Number: {network['block_number']}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 3. List existing wallets
    print("3️⃣  Listing wallets...")
    try:
        wallets = client.list_wallets()
        print(f"   Found {wallets['count']} wallet(s): {wallets['wallets']}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 4. Create or load wallet
    wallet_name = "demo_wallet"
    print(f"4️⃣  Creating wallet '{wallet_name}'...")
    try:
        wallet = client.create_wallet(wallet_name)
        print(f"   ✅ Wallet created!")
        print(f"   Address: {wallet['address']}")
        print(f"   Network: {wallet['network']}")
        print()
    except Exception as e:
        # Wallet might already exist, try to load it
        print(f"   Wallet exists, loading...")
        try:
            wallet = client.load_wallet(wallet_name)
            print(f"   ✅ Wallet loaded!")
            print(f"   Address: {wallet['address']}")
            print()
        except Exception as e2:
            print(f"   ❌ Error: {e2}")
            return
    
    # 5. Get current wallet
    print("5️⃣  Getting current wallet...")
    try:
        current = client.get_current_wallet()
        print(f"   Address: {current['address']}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 6. Get balance
    print("6️⃣  Checking balance...")
    try:
        balance = client.get_balance()
        print(f"   Address: {balance['address']}")
        print(f"   Balance: {balance['balance_ether']} {balance['currency']}")
        print(f"   Balance (Wei): {balance['balance_wei']}")
        
        if balance['balance_ether'] == 0:
            print()
            print(f"   💡 Tip: Get testnet {balance['currency']} from a faucet:")
            if balance['network'] == 'sepolia':
                print(f"      - https://sepoliafaucet.com")
                print(f"      - https://www.alchemy.com/faucets/ethereum-sepolia")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    # 7. Get transaction history
    print("7️⃣  Getting transaction history...")
    try:
        history = client.get_transaction_history()
        print(f"   Transaction Count: {history['transaction_count']}")
        print(f"   Explorer: {history['explorer_url']}")
        print(f"   Note: {history['note']}")
        print()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return
    
    print("=" * 60)
    print("✅ Demo completed successfully!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("  - Fund your wallet with testnet tokens")
    print("  - Explore the interactive API docs: http://localhost:8000/docs")
    print("  - Check out the full API reference in SETUP.md")
    print()


if __name__ == "__main__":
    main()

