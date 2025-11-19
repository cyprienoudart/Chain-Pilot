#!/usr/bin/env python3
"""
ChainPilot - Simple startup script
Run this to start the API server
"""
import sys
import os

def main():
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found!")
        print("")
        print("Quick setup:")
        print("  1. cp .env.example .env")
        print("  2. Edit .env and add your RPC URL")
        print("  3. Run this script again")
        sys.exit(1)
    
    print("🚀 Starting ChainPilot API...")
    print("📚 Docs will be at: http://localhost:8000/docs")
    print("")
    
    # Start uvicorn
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()

