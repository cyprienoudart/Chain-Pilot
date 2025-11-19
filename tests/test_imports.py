#!/usr/bin/env python3
"""
Quick test script to verify all imports work
Run this before starting the server
"""
import sys

def test_imports():
    print("🧪 Testing imports...")
    print()
    
    errors = []
    
    # Test 1: Basic imports
    try:
        import fastapi
        print("✅ FastAPI imported")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        errors.append("fastapi")
    
    # Test 2: Web3
    try:
        from web3 import Web3
        print("✅ Web3 imported")
    except ImportError as e:
        print(f"❌ Web3 import failed: {e}")
        errors.append("web3")
    
    # Test 3: Cryptography
    try:
        from cryptography.fernet import Fernet
        from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
        print("✅ Cryptography imported")
    except ImportError as e:
        print(f"❌ Cryptography import failed: {e}")
        errors.append("cryptography")
    
    # Test 4: Eth Account
    try:
        from eth_account import Account
        print("✅ Eth-account imported")
    except ImportError as e:
        print(f"❌ Eth-account import failed: {e}")
        errors.append("eth-account")
    
    # Test 5: Pydantic
    try:
        from pydantic import BaseModel
        print("✅ Pydantic imported")
    except ImportError as e:
        print(f"❌ Pydantic import failed: {e}")
        errors.append("pydantic")
    
    # Test 6: Python-dotenv
    try:
        from dotenv import load_dotenv
        print("✅ Python-dotenv imported")
    except ImportError as e:
        print(f"❌ Python-dotenv import failed: {e}")
        errors.append("python-dotenv")
    
    print()
    
    # Test 7: Our modules
    try:
        from src.execution.web3_connection import Web3Manager
        print("✅ Web3Manager imported")
    except ImportError as e:
        print(f"❌ Web3Manager import failed: {e}")
        errors.append("Web3Manager")
    
    try:
        from src.execution.secure_execution import WalletManager
        print("✅ WalletManager imported")
    except ImportError as e:
        print(f"❌ WalletManager import failed: {e}")
        errors.append("WalletManager")
    
    try:
        from src.api.routes import router
        print("✅ API routes imported")
    except ImportError as e:
        print(f"❌ API routes import failed: {e}")
        errors.append("routes")
    
    try:
        from src.api.main import app
        print("✅ FastAPI app imported")
    except ImportError as e:
        print(f"❌ FastAPI app import failed: {e}")
        errors.append("main")
    
    print()
    print("=" * 50)
    
    if errors:
        print(f"❌ {len(errors)} import(s) failed: {', '.join(errors)}")
        print()
        print("Fix:")
        print("  source .venv/bin/activate")
        print("  pip install -r requirements.txt")
        return False
    else:
        print("✅ All imports successful!")
        print()
        print("You're ready to run:")
        print("  python3 run.py")
        return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)

