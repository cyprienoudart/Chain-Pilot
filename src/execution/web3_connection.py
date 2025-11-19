"""
Web3 Connection Manager
Handles blockchain network connections and RPC management
"""
import os
import logging
from typing import Optional, Dict, Any
from web3 import Web3, AsyncWeb3
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class Web3Manager:
    """
    Manages Web3 connections to blockchain networks
    Supports multiple networks with fallback RPC endpoints
    """
    
    SUPPORTED_NETWORKS = {
        "sepolia": {
            "name": "Sepolia Testnet",
            "chain_id": 11155111,
            "currency": "ETH",
            "explorer": "https://sepolia.etherscan.io"
        },
        "polygon_mumbai": {
            "name": "Polygon Mumbai Testnet",
            "chain_id": 80001,
            "currency": "MATIC",
            "explorer": "https://mumbai.polygonscan.com"
        },
        "ethereum": {
            "name": "Ethereum Mainnet",
            "chain_id": 1,
            "currency": "ETH",
            "explorer": "https://etherscan.io"
        },
        "polygon": {
            "name": "Polygon Mainnet",
            "chain_id": 137,
            "currency": "MATIC",
            "explorer": "https://polygonscan.com"
        }
    }
    
    def __init__(self, network: Optional[str] = None, rpc_url: Optional[str] = None):
        """
        Initialize Web3 manager
        
        Args:
            network: Network name (e.g., 'sepolia', 'polygon_mumbai')
            rpc_url: Custom RPC URL (overrides network default)
        """
        self.network = network or os.getenv("WEB3_NETWORK", "sepolia")
        self.rpc_url = rpc_url or os.getenv("WEB3_RPC_URL")
        
        if not self.rpc_url:
            raise ValueError(
                "RPC URL not provided. Set WEB3_RPC_URL environment variable "
                "or pass rpc_url parameter."
            )
        
        self.w3: Optional[Web3] = None
        self.network_info = self.SUPPORTED_NETWORKS.get(self.network, {})
        
        logger.info(f"Initializing Web3Manager for network: {self.network}")
    
    async def connect(self) -> bool:
        """
        Establish connection to blockchain network
        
        Returns:
            bool: True if connection successful
        """
        try:
            logger.info(f"Connecting to {self.network} via {self.rpc_url[:50]}...")
            
            # Create Web3 instance
            if self.rpc_url.startswith("ws"):
                from web3.providers import WebsocketProvider
                provider = WebsocketProvider(self.rpc_url)
            else:
                from web3.providers import HTTPProvider
                provider = HTTPProvider(self.rpc_url)
            
            self.w3 = Web3(provider)
            
            # Add PoA middleware for some networks (like Polygon)
            if self.network in ["polygon", "polygon_mumbai"]:
                self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            # Test connection
            if not self.w3.is_connected():
                raise ConnectionError("Failed to connect to Web3 provider")
            
            # Verify network
            chain_id = self.w3.eth.chain_id
            expected_chain_id = self.network_info.get("chain_id")
            
            if expected_chain_id and chain_id != expected_chain_id:
                logger.warning(
                    f"Chain ID mismatch: expected {expected_chain_id}, got {chain_id}"
                )
            
            logger.info(
                f"Connected to {self.network_info.get('name', self.network)} "
                f"(Chain ID: {chain_id})"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Web3: {e}")
            raise
    
    async def disconnect(self):
        """Close Web3 connection"""
        if self.w3 and hasattr(self.w3.provider, 'disconnect'):
            await self.w3.provider.disconnect()
        logger.info("Web3 connection closed")
    
    def is_connected(self) -> bool:
        """Check if Web3 is connected"""
        return self.w3 is not None and self.w3.is_connected()
    
    def get_network_info(self) -> Dict[str, Any]:
        """Get current network information"""
        if not self.is_connected():
            return {"status": "disconnected"}
        
        return {
            "network": self.network,
            "name": self.network_info.get("name", "Unknown"),
            "chain_id": self.w3.eth.chain_id,
            "currency": self.network_info.get("currency", "ETH"),
            "block_number": self.w3.eth.block_number,
            "gas_price": self.w3.eth.gas_price,
            "explorer": self.network_info.get("explorer")
        }
    
    def get_balance(self, address: str) -> int:
        """
        Get native token balance for an address
        
        Args:
            address: Ethereum address
            
        Returns:
            int: Balance in wei
        """
        if not self.is_connected():
            raise ConnectionError("Web3 not connected")
        
        checksum_address = self.w3.to_checksum_address(address)
        return self.w3.eth.get_balance(checksum_address)
    
    def get_transaction_count(self, address: str) -> int:
        """
        Get transaction count (nonce) for an address
        
        Args:
            address: Ethereum address
            
        Returns:
            int: Transaction count
        """
        if not self.is_connected():
            raise ConnectionError("Web3 not connected")
        
        checksum_address = self.w3.to_checksum_address(address)
        return self.w3.eth.get_transaction_count(checksum_address)
    
    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """
        Get transaction details
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            dict: Transaction details
        """
        if not self.is_connected():
            raise ConnectionError("Web3 not connected")
        
        return dict(self.w3.eth.get_transaction(tx_hash))
    
    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get transaction receipt
        
        Args:
            tx_hash: Transaction hash
            
        Returns:
            dict: Transaction receipt or None if not mined
        """
        if not self.is_connected():
            raise ConnectionError("Web3 not connected")
        
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
            return dict(receipt) if receipt else None
        except Exception:
            return None
    
    def wei_to_ether(self, wei: int) -> float:
        """Convert wei to ether"""
        return float(self.w3.from_wei(wei, 'ether'))
    
    def ether_to_wei(self, ether: float) -> int:
        """Convert ether to wei"""
        return self.w3.to_wei(ether, 'ether')

