"""
Sandbox Mode - Simulate blockchain transactions without real network interaction
Perfect for testing without spending testnet funds
"""
import logging
import random
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class SandboxWeb3Manager:
    """
    Simulates Web3 operations for testing
    """
    
    def __init__(self):
        self.network = "sandbox"
        self.network_info = {
            "name": "Sandbox Network",
            "chain_id": 99999,
            "currency": "ETH",
            "explorer": "https://sandbox.local"
        }
        self.balances = {}  # Store simulated balances
        self.transactions = {}  # Store simulated transactions
        self.nonces = {}  # Store nonces
        logger.info("Sandbox Web3 Manager initialized")
    
    async def connect(self):
        """Simulate connection"""
        logger.info("Sandbox mode: Simulating Web3 connection")
        return True
    
    async def disconnect(self):
        """Simulate disconnection"""
        logger.info("Sandbox mode: Disconnecting")
    
    def is_connected(self) -> bool:
        """Always connected in sandbox"""
        return True
    
    def get_network_info(self) -> Dict[str, Any]:
        """Return sandbox network info"""
        return {
            **self.network_info,
            "block_number": random.randint(10000000, 20000000),
            "gas_price": 20000000000,  # 20 gwei
            "status": "sandbox"
        }
    
    def get_balance(self, address: str) -> int:
        """Return simulated balance (100 ETH by default)"""
        if address not in self.balances:
            self.balances[address] = 100000000000000000000  # 100 ETH in wei
        return self.balances[address]
    
    def get_transaction_count(self, address: str) -> int:
        """Return simulated nonce"""
        if address not in self.nonces:
            self.nonces[address] = 0
        return self.nonces[address]
    
    def wei_to_ether(self, wei: int) -> float:
        """Convert wei to ether"""
        return float(wei) / 1e18
    
    def ether_to_wei(self, ether: float) -> int:
        """Convert ether to wei"""
        return int(ether * 1e18)
    
    def to_checksum_address(self, address: str) -> str:
        """Return address as-is in sandbox"""
        # Simple checksum simulation - just ensure it starts with 0x
        if not address.startswith('0x'):
            return '0x' + address
        return address
    
    def to_wei(self, amount: float, unit: str) -> int:
        """Convert to wei"""
        return self.ether_to_wei(amount)
    
    class W3:
        """Mock web3 object"""
        def __init__(self, parent):
            self.parent = parent
            
        class eth:
            chain_id = 99999
            
            @staticmethod
            def estimate_gas(params):
                """Return reasonable gas estimate"""
                return 21000
            
            @staticmethod
            def get_transaction_count(address):
                return 0
            
            @property
            def gas_price(self):
                return 20000000000
        
        def to_checksum_address(self, address: str) -> str:
            """Return address as-is in sandbox"""
            if not address.startswith('0x'):
                return '0x' + address
            return address
        
        def to_wei(self, amount: float, unit: str) -> int:
            """Convert to wei"""
            return int(amount * 1e18)
    
    @property
    def w3(self):
        """Return mock w3 object"""
        return self.W3(self)


class SandboxWalletManager:
    """
    Extends wallet manager with sandbox capabilities
    """
    
    @staticmethod
    def sign_transaction_sandbox(transaction: Dict[str, Any]) -> str:
        """Simulate transaction signing"""
        # Generate a fake transaction hash
        tx_hash = f"0x{''.join(random.choices('0123456789abcdef', k=64))}"
        logger.info(f"Sandbox: Simulated transaction signing → {tx_hash}")
        return tx_hash
    
    @staticmethod
    def send_transaction_sandbox(signed_transaction: str) -> str:
        """Simulate transaction broadcasting"""
        # Return the "signed transaction" as tx hash
        logger.info(f"Sandbox: Simulated transaction broadcast → {signed_transaction}")
        return signed_transaction
    
    @staticmethod
    def wait_for_receipt_sandbox(tx_hash: str, timeout: int = 120) -> Dict[str, Any]:
        """Simulate transaction confirmation"""
        # Simulate network delay
        time.sleep(0.1)
        
        logger.info(f"Sandbox: Simulated transaction confirmed → {tx_hash}")
        
        return {
            'transactionHash': tx_hash,
            'blockNumber': random.randint(10000000, 20000000),
            'gasUsed': 21000,
            'status': 1,  # Success
            'from': '0x' + '0' * 40,
            'to': '0x' + '0' * 40
        }


class SandboxTransactionBuilder:
    """
    Extends transaction builder for sandbox
    """
    
    @staticmethod
    def simulate_transaction_sandbox(
        from_address: str,
        to_address: str,
        value: int
    ) -> Dict[str, Any]:
        """Simulate transaction without blockchain"""
        gas_estimate = 21000
        gas_price = 20000000000
        gas_cost = gas_estimate * gas_price
        total_cost = value + gas_cost
        
        # Assume 100 ETH balance
        balance = 100000000000000000000
        has_sufficient = balance >= total_cost
        
        return {
            'success': True,
            'can_execute': has_sufficient,
            'gas_estimate': gas_estimate,
            'gas_price': gas_price,
            'gas_cost_wei': str(gas_cost),
            'gas_cost_ether': gas_cost / 1e18,
            'total_cost_wei': str(total_cost),
            'total_cost_ether': total_cost / 1e18,
            'balance_wei': str(balance),
            'balance_ether': balance / 1e18,
            'has_sufficient_balance': has_sufficient,
            'sandbox_mode': True
        }


class SandboxTokenManager:
    """
    Simulates token operations
    """
    
    # Known test tokens
    TEST_TOKENS = {
        "0xtest_usdc": {
            "name": "USD Coin (Sandbox)",
            "symbol": "USDC",
            "decimals": 6
        },
        "0xtest_dai": {
            "name": "Dai Stablecoin (Sandbox)",
            "symbol": "DAI",
            "decimals": 18
        }
    }
    
    @staticmethod
    def get_token_info_sandbox(token_address: str) -> Dict[str, Any]:
        """Get simulated token info"""
        if token_address.lower() in [k.lower() for k in SandboxTokenManager.TEST_TOKENS]:
            for addr, info in SandboxTokenManager.TEST_TOKENS.items():
                if addr.lower() == token_address.lower():
                    return {
                        'address': token_address,
                        **info
                    }
        
        # Default for unknown tokens
        return {
            'address': token_address,
            'name': 'Test Token',
            'symbol': 'TEST',
            'decimals': 18
        }
    
    @staticmethod
    def get_token_balance_sandbox(wallet_address: str, token_address: str) -> Dict[str, Any]:
        """Get simulated token balance"""
        info = SandboxTokenManager.get_token_info_sandbox(token_address)
        
        # Simulate 1000 tokens
        balance_raw = 1000 * (10 ** info['decimals'])
        balance = 1000.0
        
        return {
            'wallet_address': wallet_address,
            'token_address': token_address,
            'token_name': info['name'],
            'token_symbol': info['symbol'],
            'decimals': info['decimals'],
            'balance': balance,
            'balance_raw': str(balance_raw),
            'sandbox_mode': True
        }


def is_sandbox_mode() -> bool:
    """Check if sandbox mode is enabled"""
    return os.environ.get('CHAINPILOT_SANDBOX', '').lower() == 'true'


def get_sandbox_banner() -> str:
    """Get sandbox mode banner for API responses"""
    return """
    ╔════════════════════════════════════════╗
    ║        🏖️  SANDBOX MODE ACTIVE        ║
    ║                                        ║
    ║  All transactions are SIMULATED       ║
    ║  No real blockchain interaction       ║
    ║  Perfect for testing!                 ║
    ╚════════════════════════════════════════╝
    """


import os

