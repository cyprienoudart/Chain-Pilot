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
    
    def import_wallet(self, wallet_name: str, private_key: str) -> Dict[str, Any]:
        """
        Import an existing wallet from private key
        
        Args:
            wallet_name: Name for the imported wallet
            private_key: Private key (with or without 0x prefix)
            
        Returns:
            dict: Wallet information (without private key)
        """
        try:
            logger.info(f"Importing wallet: {wallet_name}")
            
            # Clean private key (remove 0x if present)
            if private_key.startswith('0x'):
                private_key = private_key[2:]
            
            # Create account from private key
            account = Account.from_key(private_key)
            
            # Generate salt for encryption
            salt = os.urandom(16)
            
            # Derive encryption key
            encryption_key = self._derive_key(self.master_password, salt)
            cipher = Fernet(encryption_key)
            
            # Encrypt private key
            encrypted_key = cipher.encrypt(('0x' + private_key).encode())
            
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
            
            logger.info(f"Wallet imported successfully: {account.address}")
            
            # Get network info
            try:
                network_info = self.web3_manager.get_network_info()
                network_name = network_info.get('name', 'Unknown')
            except:
                network_name = 'Unknown'
            
            return {
                "wallet_name": wallet_name,
                "address": account.address,
                "network": network_name,
                "wallet_path": str(wallet_path)
            }
        except Exception as e:
            logger.error(f"Failed to import wallet: {e}")
            raise ValueError(f"Wallet import failed: {str(e)}")
    
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
    
    def sign_transaction(self, transaction: Dict[str, Any]) -> str:
        """
        Sign a transaction with the current wallet
        
        Args:
            transaction: Transaction dictionary
            
        Returns:
            str: Signed transaction (hex encoded)
        """
        if not self.current_wallet:
            raise ValueError("No wallet loaded. Please load or create a wallet first.")
        
        try:
            # Sign the transaction
            signed_tx = self.web3_manager.w3.eth.account.sign_transaction(
                transaction,
                private_key=self.current_wallet.key
            )
            
            logger.info(f"Transaction signed by {self.current_wallet.address[:10]}...")
            
            # Return raw signed transaction
            return signed_tx.raw_transaction.hex()
            
        except Exception as e:
            logger.error(f"Failed to sign transaction: {e}")
            raise
    
    def send_transaction(self, signed_transaction: str) -> str:
        """
        Broadcast a signed transaction
        
        Args:
            signed_transaction: Hex encoded signed transaction
            
        Returns:
            str: Transaction hash
        """
        try:
            # Send the signed transaction
            tx_hash = self.web3_manager.w3.eth.send_raw_transaction(signed_transaction)
            tx_hash_hex = tx_hash.hex()
            
            logger.info(f"Transaction sent: {tx_hash_hex}")
            return tx_hash_hex
            
        except Exception as e:
            logger.error(f"Failed to send transaction: {e}")
            raise
    
    def wait_for_transaction_receipt(
        self,
        tx_hash: str,
        timeout: int = 120
    ) -> Dict[str, Any]:
        """
        Wait for transaction confirmation
        
        Args:
            tx_hash: Transaction hash
            timeout: Timeout in seconds
            
        Returns:
            dict: Transaction receipt
        """
        try:
            logger.info(f"Waiting for transaction {tx_hash} to be confirmed...")
            
            receipt = self.web3_manager.w3.eth.wait_for_transaction_receipt(
                tx_hash,
                timeout=timeout
            )
            
            logger.info(
                f"Transaction confirmed in block {receipt['blockNumber']}, "
                f"status: {'SUCCESS' if receipt['status'] == 1 else 'FAILED'}"
            )
            
            return dict(receipt)
            
        except Exception as e:
            logger.error(f"Failed to get transaction receipt: {e}")
            raise

