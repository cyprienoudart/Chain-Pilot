"""
Rule Management API Routes - Phase 3
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Phase 3: Rules & Risk"])


class RuleCreateRequest(BaseModel):
    rule_type: str = Field(..., description="Type of rule (spending_limit, address_whitelist, etc.)")
    rule_name: str = Field(..., description="Human-readable name for the rule")
    parameters: Dict[str, Any] = Field(..., description="Rule parameters")
    action: str = Field("deny", description="Action to take: allow, deny, require_approval")
    enabled: bool = Field(True, description="Whether rule is enabled")
    priority: int = Field(0, description="Rule priority (higher = evaluated first)")


class RuleUpdateRequest(BaseModel):
    enabled: Optional[bool] = None
    parameters: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None


@router.post("/rules/create", summary="Create a new rule")
async def create_rule(request: Request, rule_request: RuleCreateRequest):
    """
    Create a new automated rule
    
    **Rule Types:**
    - `spending_limit`: Limit spending per transaction/daily/weekly/monthly
    - `address_whitelist`: Only allow transactions to specific addresses
    - `address_blacklist`: Block transactions to specific addresses
    - `time_restriction`: Only allow transactions during specific hours
    - `amount_threshold`: Require approval for amounts above threshold
    - `daily_transaction_count`: Limit number of transactions per day
    
    **Actions:**
    - `allow`: Explicitly allow (override other rules)
    - `deny`: Block transaction
    - `require_approval`: Flag for manual approval
    
    **Examples:**
    ```json
    {
      "rule_type": "spending_limit",
      "rule_name": "Daily spend limit",
      "parameters": {"type": "daily", "amount": 1.0},
      "action": "deny"
    }
    
    {
      "rule_type": "address_whitelist",
      "rule_name": "Trusted addresses",
      "parameters": {"addresses": ["0x123...", "0x456..."]},
      "action": "allow"
    }
    
    {
      "rule_type": "amount_threshold",
      "rule_name": "Large transaction approval",
      "parameters": {"threshold": 0.5},
      "action": "require_approval"
    }
    ```
    """
    try:
        rule_engine = request.app.state.rule_engine
        
        rule_id = rule_engine.create_rule(
            rule_type=rule_request.rule_type,
            rule_name=rule_request.rule_name,
            parameters=rule_request.parameters,
            action=rule_request.action,
            enabled=rule_request.enabled,
            priority=rule_request.priority
        )
        
        return {
            "message": "Rule created successfully",
            "rule_id": rule_id,
            "rule_name": rule_request.rule_name,
            "rule_type": rule_request.rule_type,
            "enabled": rule_request.enabled
        }
    except Exception as e:
        logger.error(f"Failed to create rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules", summary="Get all rules")
async def get_rules(request: Request, enabled_only: bool = False):
    """
    Get all rules
    
    **Query Parameters:**
    - `enabled_only`: Only return enabled rules (default: false)
    """
    try:
        rule_engine = request.app.state.rule_engine
        rules_list = rule_engine.get_rules(enabled_only=enabled_only)
        
        rules_data = [
            {
                "rule_id": rule.rule_id,
                "rule_type": rule.rule_type.value,
                "rule_name": rule.rule_name,
                "parameters": rule.parameters,
                "action": rule.action.value,
                "enabled": rule.enabled,
                "priority": rule.priority
            }
            for rule in rules_list
        ]
        
        return {
            "message": "Rules retrieved",
            "count": len(rules_data),
            "rules": rules_data
        }
    except Exception as e:
        logger.error(f"Failed to get rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/rules/{rule_id}", summary="Update a rule")
async def update_rule(request: Request, rule_id: int, update_request: RuleUpdateRequest):
    """
    Update an existing rule
    
    **What you can update:**
    - `enabled`: Enable/disable rule
    - `parameters`: Modify rule parameters
    - `priority`: Change evaluation priority
    """
    try:
        rule_engine = request.app.state.rule_engine
        
        updated = rule_engine.update_rule(
            rule_id=rule_id,
            enabled=update_request.enabled,
            parameters=update_request.parameters,
            priority=update_request.priority
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
        
        return {
            "message": "Rule updated successfully",
            "rule_id": rule_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rules/{rule_id}", summary="Delete a rule")
async def delete_rule(request: Request, rule_id: int):
    """
    Delete a rule
    """
    try:
        rule_engine = request.app.state.rule_engine
        
        deleted = rule_engine.delete_rule(rule_id)
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Rule {rule_id} not found")
        
        return {
            "message": "Rule deleted successfully",
            "rule_id": rule_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rules/evaluate", summary="Evaluate a transaction against rules")
async def evaluate_transaction(
    request: Request,
    to_address: str,
    value: float,
    from_address: Optional[str] = None
):
    """
    Evaluate a transaction against all rules WITHOUT executing it
    
    **Use this to:**
    - Check if a transaction would be allowed
    - See which rules would fail
    - Get risk assessment
    - Plan transactions within limits
    
    **Returns:**
    - `allowed`: Whether transaction would be allowed
    - `action`: allow, deny, require_approval
    - `risk_level`: low, medium, high, critical
    - `failed_rules`: List of rules that failed
    - `reasons`: Why each rule failed
    """
    try:
        rule_engine = request.app.state.rule_engine
        wallet_manager = request.app.state.wallet_manager
        
        # Get from_address if not provided
        if not from_address:
            if not wallet_manager.current_wallet:
                raise HTTPException(status_code=400, detail="No wallet loaded and no from_address provided")
            from_address = wallet_manager.current_wallet.address
        
        transaction = {
            "from_address": from_address,
            "to_address": to_address,
            "value": value
        }
        
        result = rule_engine.evaluate_transaction(transaction)
        
        return {
            "message": "Transaction evaluated",
            "transaction": transaction,
            **result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to evaluate transaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rules/templates", summary="Get rule templates")
async def get_rule_templates():
    """
    Get pre-configured rule templates for common scenarios
    
    **Templates include:**
    - Daily spending limits
    - Whitelist for trusted addresses
    - Large transaction approval
    - Business hours only
    - Transaction count limits
    """
    templates = [
        {
            "name": "Daily Spending Limit (1 ETH)",
            "description": "Block transactions that would exceed 1 ETH per day",
            "rule_type": "spending_limit",
            "parameters": {"type": "daily", "amount": 1.0},
            "action": "deny"
        },
        {
            "name": "Per-Transaction Limit (0.1 ETH)",
            "description": "Block any single transaction over 0.1 ETH",
            "rule_type": "spending_limit",
            "parameters": {"type": "per_transaction", "amount": 0.1},
            "action": "deny"
        },
        {
            "name": "Large Transaction Approval (0.5 ETH)",
            "description": "Require manual approval for transactions over 0.5 ETH",
            "rule_type": "amount_threshold",
            "parameters": {"threshold": 0.5},
            "action": "require_approval"
        },
        {
            "name": "Business Hours Only",
            "description": "Only allow transactions 9 AM - 5 PM UTC",
            "rule_type": "time_restriction",
            "parameters": {"allowed_hours": "09:00-17:00", "timezone": "UTC"},
            "action": "deny"
        },
        {
            "name": "Daily Transaction Limit (10)",
            "description": "Block more than 10 transactions per day",
            "rule_type": "daily_transaction_count",
            "parameters": {"max_count": 10},
            "action": "deny"
        },
        {
            "name": "Trusted Addresses Whitelist",
            "description": "Only allow transactions to pre-approved addresses",
            "rule_type": "address_whitelist",
            "parameters": {"addresses": []},  # User must add addresses
            "action": "deny"
        }
    ]
    
    return {
        "message": "Rule templates retrieved",
        "count": len(templates),
        "templates": templates
    }

