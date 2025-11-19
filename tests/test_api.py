"""
ChainPilot API Tests - Phase 1
Tests for core wallet and balance functionality
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import os

# Set test environment variables before importing app
os.environ["WEB3_NETWORK"] = "sepolia"
os.environ["WEB3_RPC_URL"] = "https://sepolia.infura.io/v3/test"
os.environ["WALLET_PASSWORD"] = "test_password"
os.environ["WALLET_DIR"] = "./test_wallets"


class TestAPIEndpoints:
    """Test API endpoints"""
    
    @pytest.fixture
    def mock_web3_manager(self):
        """Mock Web3Manager"""
        mock = Mock()
        mock.is_connected.return_value = True
        mock.network = "sepolia"
        mock.network_info = {
            "name": "Sepolia Testnet",
            "chain_id": 11155111,
            "currency": "ETH"
        }
        mock.get_network_info.return_value = {
            "network": "sepolia",
            "name": "Sepolia Testnet",
            "chain_id": 11155111,
            "currency": "ETH",
            "block_number": 12345,
            "gas_price": 1000000000
        }
        return mock
    
    @pytest.fixture
    def mock_wallet_manager(self, mock_web3_manager):
        """Mock WalletManager"""
        mock = Mock()
        mock.web3_manager = mock_web3_manager
        mock.create_wallet.return_value = {
            "wallet_name": "test_wallet",
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
            "wallet_path": "./test_wallets/test_wallet.json",
            "network": "sepolia"
        }
        mock.get_current_wallet.return_value = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
        mock.get_balance.return_value = {
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
            "balance_wei": 1000000000000000000,
            "balance_ether": 1.0,
            "currency": "ETH",
            "network": "sepolia"
        }
        mock.list_wallets.return_value = ["test_wallet", "default"]
        return mock
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        from src.api.main import app
        
        with patch('src.api.main.web3_manager') as mock_web3, \
             patch('src.api.main.wallet_manager') as mock_wallet:
            
            client = TestClient(app)
            response = client.get("/")
            
            assert response.status_code == 200
            assert response.json()["name"] == "ChainPilot API"
            assert response.json()["status"] == "running"
    
    def test_health_check(self, mock_web3_manager):
        """Test health check endpoint"""
        from src.api.main import app
        
        with patch('src.api.main.web3_manager', mock_web3_manager), \
             patch('src.api.main.wallet_manager', Mock()):
            
            client = TestClient(app)
            response = client.get("/health")
            
            assert response.status_code == 200
            data = response.json()
            assert data["web3_connected"] is True


class TestWalletEndpoints:
    """Test wallet management endpoints"""
    
    @pytest.fixture
    def client(self, mock_web3_manager, mock_wallet_manager):
        """Create test client with mocked dependencies"""
        from src.api.main import app
        
        # Mock the app state
        app.state.web3_manager = mock_web3_manager
        app.state.wallet_manager = mock_wallet_manager
        
        return TestClient(app)
    
    @pytest.fixture
    def mock_web3_manager(self):
        """Mock Web3Manager"""
        mock = Mock()
        mock.is_connected.return_value = True
        mock.network = "sepolia"
        mock.network_info = {"currency": "ETH"}
        return mock
    
    @pytest.fixture
    def mock_wallet_manager(self, mock_web3_manager):
        """Mock WalletManager"""
        mock = Mock()
        mock.web3_manager = mock_web3_manager
        mock.create_wallet.return_value = {
            "wallet_name": "test_wallet",
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
            "wallet_path": "./test_wallets/test_wallet.json",
            "network": "sepolia"
        }
        mock.get_current_wallet.return_value = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
        mock.get_balance.return_value = {
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
            "balance_wei": 1000000000000000000,
            "balance_ether": 1.0,
            "currency": "ETH",
            "network": "sepolia"
        }
        mock.get_transaction_history.return_value = {
            "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
            "transaction_count": 5,
            "network": "sepolia",
            "note": "Full transaction history requires Etherscan API integration (Phase 2)",
            "explorer_url": "https://sepolia.etherscan.io/address/0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"
        }
        mock.list_wallets.return_value = ["test_wallet", "default"]
        return mock
    
    def test_create_wallet(self, client):
        """Test wallet creation"""
        response = client.post(
            "/api/v1/wallet/create",
            json={"wallet_name": "test_wallet"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["wallet_name"] == "test_wallet"
        assert "address" in data
        assert data["network"] == "sepolia"
    
    def test_list_wallets(self, client):
        """Test listing wallets"""
        response = client.get("/api/v1/wallet/list")
        
        assert response.status_code == 200
        data = response.json()
        assert "wallets" in data
        assert data["count"] >= 0
    
    def test_get_current_wallet(self, client):
        """Test getting current wallet"""
        response = client.get("/api/v1/wallet/current")
        
        assert response.status_code == 200
        data = response.json()
        assert "address" in data
    
    def test_get_balance(self, client):
        """Test getting wallet balance"""
        response = client.get("/api/v1/wallet/balance")
        
        assert response.status_code == 200
        data = response.json()
        assert "balance_wei" in data
        assert "balance_ether" in data
        assert "address" in data
    
    def test_get_transaction_history(self, client):
        """Test getting transaction history"""
        response = client.get("/api/v1/wallet/history")
        
        assert response.status_code == 200
        data = response.json()
        assert "transaction_count" in data
        assert "address" in data
        assert "explorer_url" in data


class TestNetworkEndpoints:
    """Test network information endpoints"""
    
    @pytest.fixture
    def client(self, mock_web3_manager):
        """Create test client with mocked dependencies"""
        from src.api.main import app
        
        app.state.web3_manager = mock_web3_manager
        app.state.wallet_manager = Mock()
        
        return TestClient(app)
    
    @pytest.fixture
    def mock_web3_manager(self):
        """Mock Web3Manager"""
        mock = Mock()
        mock.is_connected.return_value = True
        mock.get_network_info.return_value = {
            "network": "sepolia",
            "name": "Sepolia Testnet",
            "chain_id": 11155111,
            "currency": "ETH",
            "block_number": 12345,
            "gas_price": 1000000000
        }
        return mock
    
    def test_get_network_info(self, client):
        """Test getting network information"""
        response = client.get("/api/v1/network/info")
        
        assert response.status_code == 200
        data = response.json()
        assert data["network"] == "sepolia"
        assert data["chain_id"] == 11155111


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

