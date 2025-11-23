"""
AI Natural Language API Routes - Phase 4
Parse natural language and execute actions
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from ..ai.intent_parser import IntentParser, Intent

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Phase 4: AI Integration"])

# Global intent parser instance
intent_parser = IntentParser()


class NaturalLanguageRequest(BaseModel):
    text: str = Field(..., description="Natural language input", min_length=1)
    execute: bool = Field(False, description="Execute the action or just parse?")
    confirm: bool = Field(True, description="Require confirmation for risky actions?")


class NameMappingRequest(BaseModel):
    name: str = Field(..., description="Friendly name (e.g., 'alice')")
    address: str = Field(..., description="Ethereum address (0x...)")


@router.post("/ai/parse", summary="Parse natural language to intent")
async def parse_natural_language(
    request: Request,
    nl_request: NaturalLanguageRequest
):
    """
    Parse natural language text into structured intent
    
    **Examples:**
    ```json
    {"text": "Send 0.5 ETH to 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"}
    {"text": "What's my balance?"}
    {"text": "Create a daily spending limit of 1 ETH"}
    {"text": "Check status of 0xabc..."}
    ```
    
    **Returns:**
    - `intent`: The detected intent (send_transaction, check_balance, etc.)
    - `entities`: Extracted entities (amount, address, etc.)
    - `confidence`: Confidence score (0-1)
    - `api_request`: Suggested API call
    - `needs_confirmation`: Whether action needs user confirmation
    """
    try:
        # Parse the text
        parsed = intent_parser.parse(nl_request.text)
        
        # Convert to API request format
        api_request = intent_parser.to_api_request(parsed)
        
        # Determine if confirmation is needed
        needs_confirmation = _needs_confirmation(parsed, nl_request.confirm)
        
        response = {
            "message": "Text parsed successfully",
            "original_text": nl_request.text,
            "intent": parsed['intent'],
            "entities": parsed['entities'],
            "confidence": parsed['confidence'],
            "parsed": parsed['parsed'],
            "api_request": api_request,
            "needs_confirmation": needs_confirmation
        }
        
        # If execute=True and high confidence, execute the action
        if nl_request.execute and parsed['confidence'] > 0.7 and api_request:
            if needs_confirmation and nl_request.confirm:
                response["message"] = "Action requires confirmation"
                response["status"] = "pending_confirmation"
            else:
                # Execute the action
                execution_result = await _execute_action(request, api_request, parsed)
                response["execution"] = execution_result
                response["status"] = "executed"
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to parse natural language: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/execute", summary="Execute parsed intent")
async def execute_parsed_intent(
    request: Request,
    intent: str,
    entities: Dict[str, Any]
):
    """
    Execute a previously parsed intent
    
    **Use this after /ai/parse when user confirms the action**
    
    Args:
        intent: The intent to execute (from parse response)
        entities: The extracted entities (from parse response)
    """
    try:
        # Reconstruct parsed format
        parsed = {
            "intent": intent,
            "entities": entities,
            "parsed": True
        }
        
        # Convert to API request
        api_request = intent_parser.to_api_request(parsed)
        
        if not api_request:
            raise HTTPException(status_code=400, detail="Cannot convert intent to API request")
        
        # Execute
        result = await _execute_action(request, api_request, parsed)
        
        return {
            "message": "Action executed successfully",
            "intent": intent,
            "result": result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute intent: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/add-name", summary="Add name-to-address mapping")
async def add_name_mapping(mapping: NameMappingRequest):
    """
    Add a friendly name mapping
    
    **Examples:**
    ```json
    {"name": "alice", "address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7"}
    {"name": "bob", "address": "0x5B38Da6a701c568545dCfcB03FcB875f56beddC4"}
    ```
    
    **Then you can say:** "Send 0.5 ETH to Alice"
    """
    try:
        # Validate address format
        if not mapping.address.startswith('0x') or len(mapping.address) != 42:
            raise HTTPException(status_code=400, detail="Invalid Ethereum address format")
        
        # Add mapping
        intent_parser.add_name_mapping(mapping.name, mapping.address)
        
        return {
            "message": f"Name mapping added: {mapping.name} → {mapping.address}",
            "name": mapping.name,
            "address": mapping.address
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add name mapping: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ai/examples", summary="Get example natural language queries")
async def get_examples():
    """
    Get example queries that can be parsed
    
    **Use these to learn what the AI can understand**
    """
    examples = [
        {
            "category": "Send Transactions",
            "examples": [
                "Send 0.5 ETH to 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb7",
                "Transfer 1.5 MATIC to 0x123...",
                "Pay 0x456... 2 ETH",
            ]
        },
        {
            "category": "Check Balance",
            "examples": [
                "What's my balance?",
                "Check balance",
                "How much ETH do I have?",
                "Show balance",
            ]
        },
        {
            "category": "Create Rules",
            "examples": [
                "Create a daily spending limit of 1 ETH",
                "Set a weekly limit to 5 ETH",
                "Limit spending to 0.5 ETH per day",
            ]
        },
        {
            "category": "Check Status",
            "examples": [
                "Check status of 0xabc123...",
                "Transaction status 0xdef456...",
                "What's the status of 0x789...",
            ]
        },
        {
            "category": "Token Balance",
            "examples": [
                "How much USDC do I have?",
                "Check DAI balance",
                "What's my USDT balance?",
            ]
        },
        {
            "category": "Wallet Management",
            "examples": [
                "Create a new wallet",
                "Create wallet",
                "Make a wallet",
            ]
        }
    ]
    
    return {
        "message": "Example queries",
        "total_categories": len(examples),
        "examples": examples
    }


# Helper functions

def _needs_confirmation(parsed: Dict[str, Any], confirm_enabled: bool) -> bool:
    """Determine if action needs user confirmation"""
    if not confirm_enabled:
        return False
    
    intent = parsed['intent']
    entities = parsed['entities']
    
    # Always confirm transactions
    if intent == Intent.SEND_TRANSACTION.value:
        # Large amounts need confirmation
        amount = entities.get('amount', 0)
        if amount > 0.1:  # More than 0.1 ETH
            return True
        return True  # All transactions need confirmation
    
    # Confirm rule creation
    if intent == Intent.CREATE_RULE.value:
        return True
    
    # Confirm wallet creation
    if intent == Intent.CREATE_WALLET.value:
        return True
    
    # Read-only operations don't need confirmation
    return False


async def _execute_action(
    request: Request,
    api_request: Dict[str, Any],
    parsed: Dict[str, Any]
) -> Dict[str, Any]:
    """Execute the API action"""
    
    intent = parsed['intent']
    entities = parsed['entities']
    endpoint = api_request['endpoint']
    params = api_request['params']
    
    logger.info(f"Executing action: {intent} via {endpoint}")
    
    try:
        # Execute based on intent
        if intent == Intent.SEND_TRANSACTION.value:
            # Use transaction send endpoint
            from .routes import send_transaction
            from ..api.routes import TransactionSendRequest
            
            tx_request = TransactionSendRequest(
                to_address=params['to_address'],
                value=params['value']
            )
            result = await send_transaction(request, tx_request)
            return {"type": "transaction", "data": result}
        
        elif intent == Intent.CHECK_BALANCE.value:
            # Use balance endpoint
            wallet_manager = request.app.state.wallet_manager
            web3_manager = request.app.state.web3_manager
            
            if not wallet_manager.current_wallet:
                raise HTTPException(status_code=400, detail="No wallet loaded")
            
            address = wallet_manager.current_wallet.address
            balance = web3_manager.get_balance(address)
            balance_ether = web3_manager.wei_to_ether(balance)
            
            return {
                "type": "balance",
                "data": {
                    "balance_wei": str(balance),
                    "balance_ether": balance_ether,
                    "currency": web3_manager.network_info.get('currency', 'ETH')
                }
            }
        
        elif intent == Intent.CREATE_RULE.value:
            # Use rules create endpoint
            rule_engine = request.app.state.rule_engine
            
            rule_id = rule_engine.create_rule(
                rule_type='spending_limit',
                rule_name=f"{params['parameters']['type'].capitalize()} Limit",
                parameters=params['parameters'],
                action='deny'
            )
            
            return {
                "type": "rule",
                "data": {
                    "rule_id": rule_id,
                    "rule_name": params['rule_name']
                }
            }
        
        elif intent == Intent.CREATE_WALLET.value:
            # Use wallet create endpoint
            wallet_manager = request.app.state.wallet_manager
            wallet_info = wallet_manager.create_wallet(params['wallet_name'])
            
            return {
                "type": "wallet",
                "data": {
                    "wallet_name": wallet_info['wallet_name'],
                    "address": wallet_info['address']
                }
            }
        
        else:
            return {
                "type": "unsupported",
                "message": f"Intent {intent} execution not yet implemented"
            }
    
    except Exception as e:
        logger.error(f"Execution failed: {e}")
        return {
            "type": "error",
            "error": str(e)
        }

