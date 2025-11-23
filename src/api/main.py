"""
ChainPilot API - Main Application
Phase 1: Core FastAPI setup with Web3 integration
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .routes import router
from .rule_routes import router as rule_router
from .ai_routes import router as ai_router
from .dashboard_routes import router as dashboard_router
from ..execution.secure_execution import WalletManager
from ..execution.web3_connection import Web3Manager
from ..execution.transaction_builder import TransactionBuilder
from ..execution.token_manager import TokenManager
from ..execution.audit_logger import AuditLogger
from ..execution.sandbox_mode import is_sandbox_mode, SandboxWeb3Manager
from ..rules.rule_engine import RuleEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
web3_manager = None
wallet_manager = None
transaction_builder = None
token_manager = None
audit_logger = None
rule_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    global web3_manager, wallet_manager, transaction_builder, token_manager, audit_logger, rule_engine
    
    logger.info("Starting ChainPilot API...")
    
    try:
        # Check for sandbox mode
        if is_sandbox_mode():
            logger.warning("🏖️  SANDBOX MODE ACTIVE - All transactions will be simulated")
            web3_manager = SandboxWeb3Manager()
            await web3_manager.connect()
            logger.info("Sandbox Web3 initialized")
        else:
            # Initialize real Web3 connection
            web3_manager = Web3Manager()
            await web3_manager.connect()
            logger.info("Web3 connection established")
        
        # Initialize wallet manager
        wallet_manager = WalletManager(web3_manager)
        logger.info("Wallet manager initialized")
        
        # Initialize transaction builder (Phase 2)
        transaction_builder = TransactionBuilder(web3_manager)
        logger.info("Transaction builder initialized")
        
        # Initialize token manager (Phase 2)
        token_manager = TokenManager(web3_manager)
        logger.info("Token manager initialized")
        
        # Initialize audit logger (Phase 2)
        audit_logger = AuditLogger()
        logger.info("Audit logger initialized")
        
        # Initialize Rule Engine
        rule_engine = RuleEngine()
        logger.info("Rule engine initialized")
        
        # Store in app state for access in routes
        app.state.web3_manager = web3_manager
        app.state.wallet_manager = wallet_manager
        app.state.transaction_builder = transaction_builder
        app.state.token_manager = token_manager
        app.state.audit_logger = audit_logger
        app.state.rule_engine = rule_engine
        
        mode = "SANDBOX" if is_sandbox_mode() else "LIVE"
        logger.info(f"ChainPilot API started successfully (Phase 5) - Mode: {mode}")
        logger.info(f"Dashboard available at: http://localhost:8000/")
        
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
app.include_router(rule_router, prefix="/api/v1")  # Phase 3: Rules
app.include_router(ai_router, prefix="/api/v1")  # Phase 4: AI Integration
app.include_router(dashboard_router)  # Phase 5: Dashboard (no prefix for root routes)


@app.get("/api")
async def api_root():
    """API root endpoint - API status"""
    return {
        "name": "ChainPilot API",
        "version": "0.1.0",
        "status": "running",
        "phase": "5 - Web Dashboard",
        "dashboard": "http://localhost:8000/",
        "api_docs": "http://localhost:8000/docs"
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

