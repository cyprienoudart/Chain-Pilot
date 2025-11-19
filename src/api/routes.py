"""
ChainPilot API Routes
Phase 1: Core wallet and balance endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class WalletCreateRequest(BaseModel):
    wallet_name: str = Field(default="default", description="Name for the wallet")


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

