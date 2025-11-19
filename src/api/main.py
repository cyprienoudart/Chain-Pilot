"""
ChainPilot API - Main Application
Phase 1: Core FastAPI setup with Web3 integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .routes import router
from ..execution.secure_execution import WalletManager
from ..execution.web3_connection import Web3Manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
web3_manager = None
wallet_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    global web3_manager, wallet_manager
    
    logger.info("Starting ChainPilot API...")
    
    try:
        # Initialize Web3 connection
        web3_manager = Web3Manager()
        await web3_manager.connect()
        logger.info("Web3 connection established")
        
        # Initialize wallet manager
        wallet_manager = WalletManager(web3_manager)
        logger.info("Wallet manager initialized")
        
        # Store in app state for access in routes
        app.state.web3_manager = web3_manager
        app.state.wallet_manager = wallet_manager
        
        logger.info("ChainPilot API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start ChainPilot API: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down ChainPilot API...")
    if web3_manager:
        await web3_manager.disconnect()
    logger.info("ChainPilot API shut down complete")


# Create FastAPI application
app = FastAPI(
    title="ChainPilot API",
    description="Secure bridge between AI agents and crypto financial systems",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint - API status"""
    return {
        "name": "ChainPilot API",
        "version": "0.1.0",
        "status": "running",
        "phase": "1 - Core Backend"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Web3 connection
        is_connected = web3_manager and web3_manager.is_connected()
        
        return {
            "status": "healthy" if is_connected else "degraded",
            "web3_connected": is_connected,
            "network": web3_manager.get_network_info() if is_connected else None
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)

