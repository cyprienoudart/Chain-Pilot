"""
ChainPilot API Routes
Phase 1: Core wallet and balance endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
import logging
from ..execution.sandbox_mode import (
    is_sandbox_mode,
    SandboxWalletManager,
    SandboxTransactionBuilder,
    SandboxTokenManager
)

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class WalletCreateRequest(BaseModel):
    wallet_name: str = Field(default="default", description="Name for the wallet")


class WalletImportRequest(BaseModel):
    wallet_name: str = Field(..., description="Name for the imported wallet")
    private_key: str = Field(..., description="Private key (with or without 0x prefix)")


class WalletCreateResponse(BaseModel):
    wallet_name: str
    address: str
    network: str
    message: str


class WalletLoadRequest(BaseModel):
    wallet_name: str = Field(default="default", description="Name of wallet to load")


class BalanceResponse(BaseModel):
    address: str
    balance_wei: int
    balance_ether: float
    currency: str
    network: str


class TransactionHistoryResponse(BaseModel):
    address: str
    transaction_count: int
    network: str
    note: str
    explorer_url: str


class WalletListResponse(BaseModel):
    wallets: list
    count: int


# Wallet Management Endpoints
@router.post("/wallet/create", response_model=WalletCreateResponse)
async def create_wallet(request: Request, body: WalletCreateRequest):
    """
    Create a new wallet with encrypted private key storage
    
    **Security**: Private keys are encrypted using PBKDF2 + Fernet encryption
    """
    try:
        wallet_manager = request.app.state.wallet_manager
        
        result = wallet_manager.create_wallet(body.wallet_name)
        
        return WalletCreateResponse(
            wallet_name=result["wallet_name"],
            address=result["address"],
            network=result["network"],
            message=f"Wallet created successfully at {result['wallet_path']}"
        )
    except Exception as e:
        logger.error(f"Failed to create wallet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wallet/import", response_model=WalletCreateResponse)
async def import_wallet(request: Request, body: WalletImportRequest):
    """
    Import an existing wallet from private key
    
    **Security**: Private key is encrypted and stored securely
    **Warning**: Never share your private key. This endpoint is for demo/testing purposes.
    """
    try:
        wallet_manager = request.app.state.wallet_manager
        
        result = wallet_manager.import_wallet(body.wallet_name, body.private_key)
        
        return WalletCreateResponse(
            wallet_name=result["wallet_name"],
            address=result["address"],
            network=result["network"],
            message=f"Wallet imported successfully at {result['wallet_path']}"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to import wallet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/wallet/load")
async def load_wallet(request: Request, body: WalletLoadRequest):
    """
    Load an existing wallet from encrypted storage
    """
    try:
        wallet_manager = request.app.state.wallet_manager
        
        result = wallet_manager.load_wallet(body.wallet_name)
        
        return {
            "wallet_name": result["wallet_name"],
            "address": result["address"],
            "network": result["network"],
            "message": "Wallet loaded successfully"
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to load wallet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wallet/list", response_model=WalletListResponse)
async def list_wallets(request: Request):
    """
    List all available wallets
    """
    try:
        wallet_manager = request.app.state.wallet_manager
        
        wallets = wallet_manager.list_wallets()
        
        return WalletListResponse(
            wallets=wallets,
            count=len(wallets)
        )
    except Exception as e:
        logger.error(f"Failed to list wallets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wallet/current")
async def get_current_wallet(request: Request):
    """
    Get currently loaded wallet address
    """
    try:
        wallet_manager = request.app.state.wallet_manager
        
        address = wallet_manager.get_current_wallet()
        
        if not address:
            raise HTTPException(status_code=404, detail="No wallet currently loaded")
        
        return {
            "address": address,
            "network": wallet_manager.web3_manager.network
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get current wallet: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Balance & History Endpoints
@router.get("/wallet/balance", response_model=BalanceResponse)
async def get_balance(
    request: Request,
    address: Optional[str] = None
):
    """
    Get native token balance for a wallet
    
    Args:
        address: Specific address to check (optional, uses current wallet if not provided)
    """
    try:
        wallet_manager = request.app.state.wallet_manager
        
        balance_info = wallet_manager.get_balance(address)
        
        return BalanceResponse(**balance_info)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wallet/history", response_model=TransactionHistoryResponse)
async def get_transaction_history(
    request: Request,
    address: Optional[str] = None,
    limit: int = 10
):
    """
    Get transaction history for a wallet
    
    **Note**: Phase 1 returns basic transaction count.
    Full history will be available in Phase 2 with Etherscan API integration.
    
    Args:
        address: Specific address to check (optional, uses current wallet if not provided)
        limit: Maximum number of transactions to return
    """
    try:
        wallet_manager = request.app.state.wallet_manager
        
        history = wallet_manager.get_transaction_history(address, limit)
        
        return TransactionHistoryResponse(**history)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get transaction history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Network Info Endpoint
@router.get("/network/info")
async def get_network_info(request: Request):
    """
    Get current blockchain network information
    """
    try:
        web3_manager = request.app.state.web3_manager
        
        if not web3_manager.is_connected():
            raise HTTPException(status_code=503, detail="Web3 not connected")
        
        return web3_manager.get_network_info()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get network info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHASE 2: Transaction Endpoints
# ============================================================================

# Request/Response Models for Transactions
class TransactionEstimateRequest(BaseModel):
    to_address: str = Field(..., description="Recipient address")
    value: float = Field(..., description="Amount in ETH/MATIC")
    data: str = Field(default="0x", description="Transaction data (optional)")


class TransactionSendRequest(BaseModel):
    to_address: str = Field(..., description="Recipient address")
    value: float = Field(..., description="Amount in ETH/MATIC")
    gas_limit: Optional[int] = Field(None, description="Gas limit (estimated if not provided)")
    gas_price: Optional[int] = Field(None, description="Gas price in wei (current if not provided)")


class TokenBalanceRequest(BaseModel):
    token_address: str = Field(..., description="Token contract address")


class TokenTransferRequest(BaseModel):
    token_address: str = Field(..., description="Token contract address")
    to_address: str = Field(..., description="Recipient address")
    amount: float = Field(..., description="Amount in token units")


class TokenApproveRequest(BaseModel):
    token_address: str = Field(..., description="Token contract address")
    spender_address: str = Field(..., description="Spender address")
    amount: float = Field(..., description="Amount to approve in token units")


@router.post("/transaction/estimate")
async def estimate_transaction(request: Request, body: TransactionEstimateRequest):
    """
    Estimate gas and cost for a transaction
    
    **Phase 2 Feature**
    """
    try:
        transaction_builder = request.app.state.transaction_builder
        wallet_manager = request.app.state.wallet_manager
        web3_manager = request.app.state.web3_manager
        
        # Get current wallet
        current_address = wallet_manager.get_current_wallet()
        if not current_address:
            raise HTTPException(status_code=400, detail="No wallet loaded")
        
        # Convert ETH to wei
        value_wei = web3_manager.ether_to_wei(body.value)
        
        # Use sandbox mode if enabled
        if is_sandbox_mode():
            from web3 import Web3
            checksum_to = Web3.to_checksum_address(body.to_address)
            estimate = SandboxTransactionBuilder.simulate_transaction_sandbox(
                from_address=current_address,
                to_address=checksum_to,
                value=value_wei
            )
            return estimate
        
        # Simulate transaction
        simulation = transaction_builder.simulate_transaction(
            current_address,
            body.to_address,
            value_wei,
            body.data
        )
        
        return simulation
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to estimate transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transaction/send")
async def send_transaction(
    request: Request,
    body: TransactionSendRequest,
    skip_rules: bool = False  # Add flag to skip rules (for testing/admin)
):
    """
    Send a native token transaction (ETH/MATIC)
    
    **Phase 2 Feature with Phase 3 Rule Enforcement**
    
    **Automatic Rule Checking:**
    - All transactions are automatically evaluated against configured rules
    - Rules can automatically DENY, ALLOW, or flag for APPROVAL
    - Risk level is calculated for every transaction
    - Use `skip_rules=true` query parameter to bypass (admin only)
    
    **What happens:**
    1. Transaction is checked against all enabled rules
    2. If any DENY rule fails → Transaction is blocked
    3. If any APPROVAL rule triggers → Returns status "requires_approval"
    4. If all rules pass → Transaction executes automatically
    5. All evaluations are logged for audit
    """
    try:
        wallet_manager = request.app.state.wallet_manager
        web3_manager = request.app.state.web3_manager
        audit_logger = request.app.state.audit_logger
        rule_engine = request.app.state.rule_engine
        
        # Get current wallet
        if not wallet_manager.current_wallet:
            raise HTTPException(status_code=400, detail="No wallet loaded")
        
        current_address = wallet_manager.current_wallet.address
        from web3 import Web3
        checksum_to = Web3.to_checksum_address(body.to_address)
        
        # PHASE 3: Rule Enforcement - Check transaction against rules
        if not skip_rules:
            transaction_to_check = {
                "from_address": current_address,
                "to_address": checksum_to,
                "value": body.value
            }
            
            rule_result = rule_engine.evaluate_transaction(transaction_to_check)
            
            # If transaction is denied by rules
            if not rule_result["allowed"]:
                # Log blocked transaction
                audit_logger.log_event("TX_BLOCKED", {
                    "from": current_address,
                    "to": checksum_to,
                    "value": body.value,
                    "risk_level": rule_result["risk_level"],
                    "failed_rules": rule_result["failed_rules"],
                    "reasons": rule_result["reasons"]
                })
                
                return {
                    "message": "Transaction blocked by rules",
                    "status": "blocked",
                    "action": rule_result["action"],
                    "risk_level": rule_result["risk_level"],
                    "failed_rules": rule_result["failed_rules"],
                    "reasons": rule_result["reasons"],
                    "rules_checked": rule_result["rules_checked"]
                }
            
            # If transaction requires approval
            if rule_result["action"] == "require_approval":
                # Log for manual review
                audit_logger.log_event("TX_REQUIRES_APPROVAL", {
                    "from": current_address,
                    "to": checksum_to,
                    "value": body.value,
                    "risk_level": rule_result["risk_level"],
                    "failed_rules": rule_result["failed_rules"]
                })
                
                return {
                    "message": "Transaction requires manual approval",
                    "status": "requires_approval",
                    "action": rule_result["action"],
                    "risk_level": rule_result["risk_level"],
                    "failed_rules": rule_result["failed_rules"],
                    "reasons": rule_result["reasons"],
                    "from_address": current_address,
                    "to_address": checksum_to,
                    "value": body.value
                }
        
        # Use sandbox mode if enabled
        if is_sandbox_mode():
            # Simulate transaction in sandbox
            tx_hash = SandboxWalletManager.sign_transaction_sandbox({
                'from': current_address,
                'to': checksum_to,
                'value': web3_manager.ether_to_wei(body.value)
            })
            
            # Log to audit
            audit_logger.log_transaction(
                tx_hash=tx_hash,
                from_address=current_address,
                to_address=checksum_to,
                value=str(body.value),
                token_address=None,
                status="confirmed"  # Instant confirmation in sandbox
            )
            
            return {
                "message": "Transaction sent successfully (SANDBOX)",
                "tx_hash": tx_hash,
                "from_address": current_address,
                "to_address": checksum_to,
                "value": body.value,
                "status": "confirmed",
                "sandbox_mode": True,
                "explorer_url": f"https://sandbox.local/tx/{tx_hash}"
            }
        
        # Real mode
        transaction_builder = request.app.state.transaction_builder
        
        # Convert ETH to wei
        value_wei = web3_manager.ether_to_wei(body.value)
        
        # Build transaction
        transaction = transaction_builder.build_transaction(
            from_address=current_address,
            to_address=checksum_to,
            value=value_wei,
            gas_limit=body.gas_limit
        )
        
        # Sign transaction
        signed_tx = wallet_manager.sign_transaction(transaction)
        
        # Send transaction
        tx_hash = await web3_manager.broadcast_raw_transaction(signed_tx)
        
        # Log to database
        audit_logger.log_transaction(
            tx_hash=tx_hash,
            from_address=current_address,
            to_address=checksum_to,
            value=str(body.value),
            token_address=None,
            status="pending"
        )
        
        # Log event
        audit_logger.log_event("TX_SENT", {
            "tx_hash": tx_hash,
            "from": current_address,
            "to": checksum_to,
            "value": body.value
        })
        
        network_info = web3_manager.get_network_info()
        explorer_url = f"{network_info.get('explorer', 'https://polygonscan.com')}/tx/{tx_hash}"
        
        return {
            "tx_hash": tx_hash,
            "status": "SUBMITTED",
            "from_address": current_address,
            "to_address": body.to_address,
            "value": body.value,
            "explorer_url": explorer_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/transaction/{tx_hash}")
async def get_transaction_status(request: Request, tx_hash: str):
    """
    Get transaction status and details
    
    **Phase 2 Feature**
    """
    try:
        web3_manager = request.app.state.web3_manager
        audit_logger = request.app.state.audit_logger
        
        # Check database first
        db_tx = audit_logger.get_transaction(tx_hash)
        
        # Try to get receipt from blockchain
        try:
            receipt = web3_manager.get_transaction_receipt(tx_hash)
            
            if receipt:
                status = "CONFIRMED" if receipt.get('status') == 1 else "FAILED"
                
                # Update database if status changed
                if db_tx and db_tx['status'] != status:
                    audit_logger.log_transaction(
                        tx_hash=tx_hash,
                        from_address=db_tx['from_address'],
                        to_address=db_tx['to_address'],
                        value=db_tx['value'],
                        status=status,
                        gas_used=receipt.get('gasUsed'),
                        block_number=receipt.get('blockNumber')
                    )
                
                return {
                    "tx_hash": tx_hash,
                    "status": status,
                    "block_number": receipt.get('blockNumber'),
                    "gas_used": receipt.get('gasUsed'),
                    "from_address": receipt.get('from'),
                    "to_address": receipt.get('to')
                }
            else:
                # Transaction pending
                return {
                    "tx_hash": tx_hash,
                    "status": "PENDING"
                }
                
        except Exception:
            # Transaction not found on chain, check database
            if db_tx:
                return {
                    "tx_hash": tx_hash,
                    "status": db_tx['status'],
                    "from_address": db_tx['from_address'],
                    "to_address": db_tx['to_address']
                }
            else:
                raise HTTPException(status_code=404, detail="Transaction not found")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transaction status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHASE 2: Token Endpoints
# ============================================================================

@router.get("/token/balance/{token_address}")
async def get_token_balance(request: Request, token_address: str):
    """
    Get ERC-20 token balance
    
    **Phase 2 Feature**
    """
    try:
        token_manager = request.app.state.token_manager
        wallet_manager = request.app.state.wallet_manager
        
        # Get current wallet
        current_address = wallet_manager.get_current_wallet()
        if not current_address:
            raise HTTPException(status_code=400, detail="No wallet loaded")
        
        # Get token balance
        balance_info = token_manager.get_token_balance(current_address, token_address)
        
        return balance_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get token balance: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token/transfer")
async def transfer_token(request: Request, body: TokenTransferRequest):
    """
    Transfer ERC-20 tokens
    
    **Phase 2 Feature**
    """
    try:
        token_manager = request.app.state.token_manager
        wallet_manager = request.app.state.wallet_manager
        audit_logger = request.app.state.audit_logger
        
        # Get current wallet
        current_address = wallet_manager.get_current_wallet()
        if not current_address:
            raise HTTPException(status_code=400, detail="No wallet loaded")
        
        # Build token transfer transaction
        tx_data = token_manager.build_transfer_transaction(
            current_address,
            body.to_address,
            body.token_address,
            body.amount
        )
        
        # Sign transaction
        signed_tx = wallet_manager.sign_transaction(tx_data['transaction'])
        
        # Send transaction
        tx_hash = wallet_manager.send_transaction(signed_tx)
        
        # Log to database
        audit_logger.log_transaction(
            tx_hash=tx_hash,
            from_address=current_address,
            to_address=body.to_address,
            value=tx_data['amount_raw'],
            status="SUBMITTED",
            token_address=body.token_address,
            token_symbol=tx_data['token_info']['symbol']
        )
        
        return {
            "tx_hash": tx_hash,
            "status": "SUBMITTED",
            "token_symbol": tx_data['token_info']['symbol'],
            "amount": body.amount
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to transfer token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/token/approve")
async def approve_token(request: Request, body: TokenApproveRequest):
    """
    Approve ERC-20 token spending
    
    **Phase 2 Feature**
    """
    try:
        token_manager = request.app.state.token_manager
        wallet_manager = request.app.state.wallet_manager
        
        # Get current wallet
        current_address = wallet_manager.get_current_wallet()
        if not current_address:
            raise HTTPException(status_code=400, detail="No wallet loaded")
        
        # Build approval transaction
        tx_data = token_manager.build_approve_transaction(
            current_address,
            body.spender_address,
            body.token_address,
            body.amount
        )
        
        # Sign transaction
        signed_tx = wallet_manager.sign_transaction(tx_data['transaction'])
        
        # Send transaction
        tx_hash = wallet_manager.send_transaction(signed_tx)
        
        return {
            "tx_hash": tx_hash,
            "status": "SUBMITTED",
            "token_symbol": tx_data['token_info']['symbol'],
            "amount": body.amount,
            "spender": body.spender_address
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve token: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# PHASE 2: Audit Endpoints
# ============================================================================

@router.get("/audit/transactions")
async def get_audit_transactions(
    request: Request,
    limit: int = 50,
    status: Optional[str] = None
):
    """
    Get transaction history from audit log
    
    **Phase 2 Feature**
    """
    try:
        audit_logger = request.app.state.audit_logger
        wallet_manager = request.app.state.wallet_manager
        
        # Get current wallet (optional filter)
        current_address = wallet_manager.get_current_wallet()
        
        # Get transactions
        transactions = audit_logger.get_transaction_history(
            from_address=current_address,
            limit=limit,
            status=status
        )
        
        return {
            "transactions": transactions,
            "count": len(transactions)
        }
        
    except Exception as e:
        logger.error(f"Failed to get audit transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/events")
async def get_audit_events(
    request: Request,
    event_type: Optional[str] = None,
    limit: int = 50
):
    """
    Get events from audit log
    
    **Phase 2 Feature**
    """
    try:
        audit_logger = request.app.state.audit_logger
        
        # Get events
        events = audit_logger.get_events(
            event_type=event_type,
            limit=limit
        )
        
        return {
            "events": events,
            "count": len(events)
        }
        
    except Exception as e:
        logger.error(f"Failed to get audit events: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/audit/statistics")
async def get_audit_statistics(request: Request):
    """
    Get transaction statistics
    
    **Phase 2 Feature**
    """
    try:
        audit_logger = request.app.state.audit_logger
        
        stats = audit_logger.get_statistics()
        
        return stats
        
    except Exception as e:
        logger.error(f"Failed to get audit statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

