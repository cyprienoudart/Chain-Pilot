# ChainPilot Examples

This directory contains example scripts demonstrating how to interact with the ChainPilot API.

## Available Examples

### `test_api_client.py`

A complete demo of the ChainPilot API functionality, showing:
- Health checks and network information
- Wallet creation and management
- Balance checking
- Transaction history queries

**Usage:**

```bash
# Make sure the API is running first
./start_api.sh

# In a new terminal, run the example (with venv activated)
python examples/test_api_client.py
```

## Using the Client

You can also import and use the `ChainPilotClient` class in your own scripts:

```python
from examples.test_api_client import ChainPilotClient

# Initialize client
client = ChainPilotClient()

# Create a wallet
wallet = client.create_wallet("my_wallet")
print(f"Created wallet: {wallet['address']}")

# Check balance
balance = client.get_balance()
print(f"Balance: {balance['balance_ether']} ETH")
```

## Interactive API Documentation

For interactive testing and exploration, use the auto-generated API docs:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These provide a web interface to test all endpoints without writing code.

## Future Examples

Coming in future phases:
- Transaction creation and signing
- Rule management
- AI agent integration examples
- Dashboard integration

