#!/usr/bin/env python3
"""
ChainPilot - Startup script with sandbox mode support
Run this to start the API server
"""
import sys
import os
import argparse

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='ChainPilot API Server')
    parser.add_argument(
        '--sandbox',
        action='store_true',
        help='Run in sandbox mode (simulated transactions, no real blockchain)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port to run server on (default: 8000)'
    )
    args = parser.parse_args()
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ Error: .env file not found!")
        print("")
        print("Quick setup:")
        print("  1. cp .env.example .env")
        print("  2. Edit .env and add your RPC URL")
        print("  3. Run this script again")
        print("")
        print("For testing without RPC:")
        print("  python3 run.py --sandbox")
        sys.exit(1)
    
    # Set sandbox mode environment variable
    if args.sandbox:
        os.environ['CHAINPILOT_SANDBOX'] = 'true'
        print("🏖️  SANDBOX MODE ENABLED")
        print("   - Transactions will be simulated")
        print("   - No real blockchain interaction")
        print("   - Perfect for testing without funds")
        print("")
    
    print("🚀 Starting ChainPilot API...")
    print(f"📚 Docs will be at: http://localhost:{args.port}/docs")
    if args.sandbox:
        print("⚠️  SANDBOX: All transactions are simulated")
    print("")
    
    # Start uvicorn
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=args.port,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
