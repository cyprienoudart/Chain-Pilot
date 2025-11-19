"""
Secure Wallet Management
Handles wallet creation, encryption, and secure key storage
"""
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from eth_account import Account
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import base64

load_dotenv()

logger = logging.getLogger(__name__)


class WalletManager:
    """
    Manages crypto wallets with encrypted private key storage
    Phase 1: Local encrypted storage
    Future: MPC wallets, hardware wallet integration
    """
    
    def __init__(self, web3_manager, wallet_dir: Optional[str] = None):
        """
        Initialize wallet manager
        
        Args:
            web3_manager: Web3Manager instance
            wallet_dir: Directory to store encrypted wallets
        """
        self.web3_manager = web3_manager
        self.wallet_dir = Path(wallet_dir or os.getenv("WALLET_DIR", "./wallets"))
        self.wallet_dir.mkdir(exist_ok=True)
        
        # Master password from environment (in production, use HSM or secret manager)
        self.master_password = os.getenv("WALLET_PASSWORD")
        if not self.master_password:
            logger.warning(
                "WALLET_PASSWORD not set. Wallet encryption will use default password. "
                "This is INSECURE for production!"
            )
            self.master_password = "changeme_insecure_default"
        
        self.current_wallet: Optional[Account] = None
        logger.info(f"Wallet manager initialized. Storage: {self.wallet_dir}")
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2
        
        Args:
            password: Master password
            salt: Salt for key derivation
            
        Returns:
            bytes: Derived key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def create_wallet(self, wallet_name: str = "default") -> Dict[str, Any]:
        """
        Create a new wallet with encrypted private key storage
        
        Args:
            wallet_name: Name for the wallet
            
        Returns:
            dict: Wallet information (without private key)
        """
        try:
            logger.info(f"Creating new wallet: {wallet_name}")
            
            # Generate new account
            account = Account.create()
            
            # Generate salt for encryption
            salt = os.urandom(16)
            
            # Derive encryption key
            encryption_key = self._derive_key(self.master_password, salt)
            cipher = Fernet(encryption_key)
            
            # Encrypt private key
            encrypted_key = cipher.encrypt(account.key.hex().encode())
            
            # Prepare wallet data
            wallet_data = {
                "address": account.address,
                "encrypted_private_key": encrypted_key.decode(),
                "salt": base64.b64encode(salt).decode(),
                "version": "1.0"
            }
            
            # Save to file
            wallet_path = self.wallet_dir / f"{wallet_name}.json"
            with open(wallet_path, 'w') as f:
                json.dump(wallet_data, f, indent=2)
            
            # Set as current wallet
            self.current_wallet = account
            
            logger.info(f"Wallet created successfully: {account.address}")
            
            return {
                "wallet_name": wallet_name,
                "address": account.address,
                "wallet_path": str(wallet_path),
                "network": self.web3_manager.network
            }
            
        except Exception as e:
            logger.error(f"Failed to create wallet: {e}")
            raise
    
    def load_wallet(self, wallet_name: str = "default") -> Dict[str, Any]:
        """
        Load an existing wallet from encrypted storage
        
        Args:
            wallet_name: Name of the wallet to load
            
        Returns:
            dict: Wallet information
        """
        try:
            wallet_path = self.wallet_dir / f"{wallet_name}.json"
            
            if not wallet_path.exists():
                raise FileNotFoundError(f"Wallet not found: {wallet_name}")
            
            logger.info(f"Loading wallet: {wallet_name}")
            
            # Read encrypted wallet data
            with open(wallet_path, 'r') as f:
                wallet_data = json.load(f)
            
            # Decrypt private key
            salt = base64.b64decode(wallet_data["salt"])
            encryption_key = self._derive_key(self.master_password, salt)
            cipher = Fernet(encryption_key)
            
            encrypted_key = wallet_data["encrypted_private_key"].encode()
            private_key = cipher.decrypt(encrypted_key).decode()
            
            # Create account from private key
            account = Account.from_key(private_key)
            
            # Verify address matches
            if account.address != wallet_data["address"]:
                raise ValueError("Address mismatch - wallet may be corrupted")
            
            self.current_wallet = account
            
            logger.info(f"Wallet loaded successfully: {account.address}")
            
            return {
                "wallet_name": wallet_name,
                "address": account.address,
                "network": self.web3_manager.network
            }
            
        except Exception as e:
            logger.error(f"Failed to load wallet: {e}")
            raise
    
    def get_current_wallet(self) -> Optional[str]:
        """Get address of currently loaded wallet"""
        return self.current_wallet.address if self.current_wallet else None
    
    def get_balance(self, address: Optional[str] = None) -> Dict[str, Any]:
        """
        Get balance for wallet
        
        Args:
            address: Address to check (uses current wallet if not provided)
            
        Returns:
            dict: Balance information
        """
        if not address:
            if not self.current_wallet:
                raise ValueError("No wallet loaded and no address provided")
            address = self.current_wallet.address
        
        # Get balance from Web3
        wei_balance = self.web3_manager.get_balance(address)
        ether_balance = self.web3_manager.wei_to_ether(wei_balance)
        
        return {
            "address": address,
            "balance_wei": wei_balance,
            "balance_ether": ether_balance,
            "currency": self.web3_manager.network_info.get("currency", "ETH"),
            "network": self.web3_manager.network
        }
    
    def get_transaction_history(
        self, 
        address: Optional[str] = None, 
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get transaction history for wallet
        Note: Phase 1 returns basic info. Future phases will integrate with Etherscan API
        
        Args:
            address: Address to check
            limit: Maximum number of transactions
            
        Returns:
            dict: Transaction history
        """
        if not address:
            if not self.current_wallet:
                raise ValueError("No wallet loaded and no address provided")
            address = self.current_wallet.address
        
        # Get transaction count
        tx_count = self.web3_manager.get_transaction_count(address)
        
        return {
            "address": address,
            "transaction_count": tx_count,
            "network": self.web3_manager.network,
            "note": "Full transaction history requires Etherscan API integration (Phase 2)",
            "explorer_url": f"{self.web3_manager.network_info.get('explorer')}/address/{address}"
        }
    
    def list_wallets(self) -> list:
        """List all available wallets"""
        wallet_files = self.wallet_dir.glob("*.json")
        return [f.stem for f in wallet_files]

