"""
Token Manager - ERC-20 token operations
"""
import logging
from typing import Dict, Any, Optional
from web3 import Web3

logger = logging.getLogger(__name__)

# Standard ERC-20 ABI (minimal interface)
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_to", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "transfer",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "_spender", "type": "address"},
            {"name": "_value", "type": "uint256"}
        ],
        "name": "approve",
        "outputs": [{"name": "", "type": "bool"}],
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [
            {"name": "_owner", "type": "address"},
            {"name": "_spender", "type": "address"}
        ],
        "name": "allowance",
        "outputs": [{"name": "", "type": "uint256"}],
        "type": "function"
    }
]


class TokenManager:
    """
    Manages ERC-20 token operations
    Handles token balances, transfers, and approvals
    """
    
    def __init__(self, web3_manager):
        """
        Initialize token manager
        
        Args:
            web3_manager: Web3Manager instance
        """
        self.web3_manager = web3_manager
        self.w3 = web3_manager.w3
        logger.info("Token manager initialized")
    
    def get_token_contract(self, token_address: str):
        """
        Get token contract instance
        
        Args:
            token_address: Token contract address
            
        Returns:
            Contract instance
        """
        checksum_address = self.w3.to_checksum_address(token_address)
        return self.w3.eth.contract(address=checksum_address, abi=ERC20_ABI)
    
    def get_token_info(self, token_address: str) -> Dict[str, Any]:
        """
        Get token metadata
        
        Args:
            token_address: Token contract address
            
        Returns:
            dict: Token name, symbol, decimals
        """
        try:
            contract = self.get_token_contract(token_address)
            
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            
            logger.info(f"Token info: {symbol} ({name}), decimals: {decimals}")
            
            return {
                'address': token_address,
                'name': name,
                'symbol': symbol,
                'decimals': decimals
            }
            
        except Exception as e:
            logger.error(f"Failed to get token info: {e}")
            raise
    
    def get_token_balance(
        self,
        wallet_address: str,
        token_address: str
    ) -> Dict[str, Any]:
        """
        Get token balance for a wallet
        
        Args:
            wallet_address: Wallet address
            token_address: Token contract address
            
        Returns:
            dict: Balance information
        """
        try:
            contract = self.get_token_contract(token_address)
            wallet_checksum = self.w3.to_checksum_address(wallet_address)
            
            # Get token info
            info = self.get_token_info(token_address)
            
            # Get balance
            balance_raw = contract.functions.balanceOf(wallet_checksum).call()
            
            # Convert to human-readable format
            balance_formatted = balance_raw / (10 ** info['decimals'])
            
            logger.info(
                f"Token balance for {wallet_address[:10]}...: "
                f"{balance_formatted} {info['symbol']}"
            )
            
            return {
                'wallet_address': wallet_address,
                'token_address': token_address,
                'token_name': info['name'],
                'token_symbol': info['symbol'],
                'decimals': info['decimals'],
                'balance': balance_formatted,
                'balance_raw': str(balance_raw)
            }
            
        except Exception as e:
            logger.error(f"Failed to get token balance: {e}")
            raise
    
    def build_transfer_transaction(
        self,
        from_address: str,
        to_address: str,
        token_address: str,
        amount: float,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build token transfer transaction
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            token_address: Token contract address
            amount: Amount in token units (e.g., 10.5 USDC)
            gas_limit: Gas limit (estimated if not provided)
            gas_price: Gas price (current if not provided)
            
        Returns:
            dict: Transaction dictionary and token info
        """
        try:
            contract = self.get_token_contract(token_address)
            info = self.get_token_info(token_address)
            
            # Convert amount to raw units
            amount_raw = int(amount * (10 ** info['decimals']))
            
            # Build transfer data
            to_checksum = self.w3.to_checksum_address(to_address)
            transfer_data = contract.functions.transfer(
                to_checksum,
                amount_raw
            ).build_transaction({
                'from': self.w3.to_checksum_address(from_address),
                'gas': gas_limit or 100000,  # Default for token transfer
                'gasPrice': gas_price or self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(
                    self.w3.to_checksum_address(from_address)
                ),
                'chainId': self.w3.eth.chain_id
            })
            
            logger.info(
                f"Token transfer built: {amount} {info['symbol']} "
                f"to {to_address[:10]}..."
            )
            
            return {
                'transaction': transfer_data,
                'token_info': info,
                'amount': amount,
                'amount_raw': str(amount_raw)
            }
            
        except Exception as e:
            logger.error(f"Failed to build token transfer: {e}")
            raise
    
    def build_approve_transaction(
        self,
        from_address: str,
        spender_address: str,
        token_address: str,
        amount: float,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build token approval transaction
        
        Args:
            from_address: Token owner address
            spender_address: Address to approve
            token_address: Token contract address
            amount: Amount to approve in token units
            gas_limit: Gas limit
            gas_price: Gas price
            
        Returns:
            dict: Transaction dictionary and token info
        """
        try:
            contract = self.get_token_contract(token_address)
            info = self.get_token_info(token_address)
            
            # Convert amount to raw units
            amount_raw = int(amount * (10 ** info['decimals']))
            
            # Build approve data
            spender_checksum = self.w3.to_checksum_address(spender_address)
            approve_data = contract.functions.approve(
                spender_checksum,
                amount_raw
            ).build_transaction({
                'from': self.w3.to_checksum_address(from_address),
                'gas': gas_limit or 60000,  # Default for approval
                'gasPrice': gas_price or self.w3.eth.gas_price,
                'nonce': self.w3.eth.get_transaction_count(
                    self.w3.to_checksum_address(from_address)
                ),
                'chainId': self.w3.eth.chain_id
            })
            
            logger.info(
                f"Token approval built: {amount} {info['symbol']} "
                f"for {spender_address[:10]}..."
            )
            
            return {
                'transaction': approve_data,
                'token_info': info,
                'amount': amount,
                'amount_raw': str(amount_raw)
            }
            
        except Exception as e:
            logger.error(f"Failed to build token approval: {e}")
            raise
    
    def get_allowance(
        self,
        owner_address: str,
        spender_address: str,
        token_address: str
    ) -> Dict[str, Any]:
        """
        Get token allowance
        
        Args:
            owner_address: Token owner address
            spender_address: Spender address
            token_address: Token contract address
            
        Returns:
            dict: Allowance information
        """
        try:
            contract = self.get_token_contract(token_address)
            info = self.get_token_info(token_address)
            
            owner_checksum = self.w3.to_checksum_address(owner_address)
            spender_checksum = self.w3.to_checksum_address(spender_address)
            
            allowance_raw = contract.functions.allowance(
                owner_checksum,
                spender_checksum
            ).call()
            
            allowance_formatted = allowance_raw / (10 ** info['decimals'])
            
            return {
                'owner': owner_address,
                'spender': spender_address,
                'token_address': token_address,
                'token_symbol': info['symbol'],
                'allowance': allowance_formatted,
                'allowance_raw': str(allowance_raw)
            }
            
        except Exception as e:
            logger.error(f"Failed to get allowance: {e}")
            raise

