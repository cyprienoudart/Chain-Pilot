"""
Transaction Builder - Build, estimate, and simulate transactions
"""
import logging
from typing import Dict, Any, Optional
from web3 import Web3

logger = logging.getLogger(__name__)


class TransactionBuilder:
    """
    Builds and estimates transactions before sending
    Handles gas estimation, nonce management, and simulation
    """
    
    def __init__(self, web3_manager):
        """
        Initialize transaction builder
        
        Args:
            web3_manager: Web3Manager instance
        """
        self.web3_manager = web3_manager
        self.w3 = web3_manager.w3
        logger.info("Transaction builder initialized")
    
    def estimate_gas(
        self,
        from_address: str,
        to_address: str,
        value: int = 0,
        data: str = "0x"
    ) -> int:
        """
        Estimate gas for a transaction
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            value: Amount in wei
            data: Transaction data (for contract calls)
            
        Returns:
            int: Estimated gas limit
        """
        try:
            from_checksum = self.w3.to_checksum_address(from_address)
            to_checksum = self.w3.to_checksum_address(to_address)
            
            gas_estimate = self.w3.eth.estimate_gas({
                'from': from_checksum,
                'to': to_checksum,
                'value': value,
                'data': data
            })
            
            # Add 10% buffer for safety
            gas_with_buffer = int(gas_estimate * 1.1)
            
            logger.info(f"Gas estimated: {gas_estimate} (with buffer: {gas_with_buffer})")
            return gas_with_buffer
            
        except Exception as e:
            logger.error(f"Gas estimation failed: {e}")
            # Return safe default for simple transfers
            if data == "0x":
                return 21000
            raise
    
    def get_nonce(self, address: str) -> int:
        """
        Get transaction nonce for an address
        
        Args:
            address: Ethereum address
            
        Returns:
            int: Nonce (transaction count)
        """
        checksum_address = self.w3.to_checksum_address(address)
        nonce = self.w3.eth.get_transaction_count(checksum_address)
        logger.debug(f"Nonce for {address}: {nonce}")
        return nonce
    
    def get_gas_price(self) -> int:
        """
        Get current gas price
        
        Returns:
            int: Gas price in wei
        """
        gas_price = self.w3.eth.gas_price
        logger.debug(f"Current gas price: {gas_price} wei")
        return gas_price
    
    def build_transaction(
        self,
        from_address: str,
        to_address: str,
        value: int,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None,
        data: str = "0x",
        nonce: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Build a transaction dictionary
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            value: Amount in wei
            gas_limit: Gas limit (estimated if not provided)
            gas_price: Gas price in wei (current price if not provided)
            data: Transaction data
            nonce: Transaction nonce (current if not provided)
            
        Returns:
            dict: Transaction dictionary ready for signing
        """
        from_checksum = self.w3.to_checksum_address(from_address)
        to_checksum = self.w3.to_checksum_address(to_address)
        
        # Get nonce if not provided
        if nonce is None:
            nonce = self.get_nonce(from_address)
        
        # Estimate gas if not provided
        if gas_limit is None:
            gas_limit = self.estimate_gas(from_address, to_address, value, data)
        
        # Get gas price if not provided
        if gas_price is None:
            gas_price = self.get_gas_price()
        
        # Build transaction
        transaction = {
            'from': from_checksum,
            'to': to_checksum,
            'value': value,
            'gas': gas_limit,
            'gasPrice': gas_price,
            'nonce': nonce,
            'chainId': self.w3.eth.chain_id,
            'data': data
        }
        
        logger.info(f"Transaction built: {from_address[:10]}... → {to_address[:10]}...")
        return transaction
    
    def simulate_transaction(
        self,
        from_address: str,
        to_address: str,
        value: int = 0,
        data: str = "0x"
    ) -> Dict[str, Any]:
        """
        Simulate a transaction (dry run)
        
        Args:
            from_address: Sender address
            to_address: Recipient address
            value: Amount in wei
            data: Transaction data
            
        Returns:
            dict: Simulation result with success status and gas estimate
        """
        try:
            from_checksum = self.w3.to_checksum_address(from_address)
            to_checksum = self.w3.to_checksum_address(to_address)
            
            # Try to estimate gas (will fail if transaction would revert)
            gas_estimate = self.w3.eth.estimate_gas({
                'from': from_checksum,
                'to': to_checksum,
                'value': value,
                'data': data
            })
            
            # Get current gas price
            gas_price = self.get_gas_price()
            
            # Calculate costs
            gas_cost_wei = gas_estimate * gas_price
            total_cost_wei = value + gas_cost_wei
            
            # Check balance
            balance = self.web3_manager.get_balance(from_address)
            has_sufficient_balance = balance >= total_cost_wei
            
            return {
                'success': True,
                'can_execute': has_sufficient_balance,
                'gas_estimate': gas_estimate,
                'gas_price': gas_price,
                'gas_cost_wei': str(gas_cost_wei),
                'gas_cost_ether': self.web3_manager.wei_to_ether(gas_cost_wei),
                'total_cost_wei': str(total_cost_wei),
                'total_cost_ether': self.web3_manager.wei_to_ether(total_cost_wei),
                'balance_wei': str(balance),
                'balance_ether': self.web3_manager.wei_to_ether(balance),
                'has_sufficient_balance': has_sufficient_balance
            }
            
        except Exception as e:
            logger.warning(f"Transaction simulation failed: {e}")
            return {
                'success': False,
                'can_execute': False,
                'error': str(e)
            }
    
    def calculate_transaction_cost(
        self,
        value: int,
        gas_limit: int,
        gas_price: int
    ) -> Dict[str, Any]:
        """
        Calculate total transaction cost
        
        Args:
            value: Amount to send in wei
            gas_limit: Gas limit
            gas_price: Gas price in wei
            
        Returns:
            dict: Cost breakdown
        """
        gas_cost = gas_limit * gas_price
        total_cost = value + gas_cost
        
        return {
            'value_wei': str(value),
            'value_ether': self.web3_manager.wei_to_ether(value),
            'gas_cost_wei': str(gas_cost),
            'gas_cost_ether': self.web3_manager.wei_to_ether(gas_cost),
            'total_cost_wei': str(total_cost),
            'total_cost_ether': self.web3_manager.wei_to_ether(total_cost),
            'currency': self.web3_manager.network_info.get('currency', 'ETH')
        }

