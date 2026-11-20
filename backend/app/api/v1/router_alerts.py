from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from backend.app.services.alerts.service import alert_engine_service, AlertEventItem, AlertRuleItem

router = APIRouter(prefix="/alerts", tags=["AI Alerts & Notifications"])

class CreateRulePayload(BaseModel):
    symbol: Optional[str] = None
    category: str
    condition_type: str
    threshold_value: float

@router.get("", response_model=List[AlertEventItem])
async def get_alerts(unread_only: bool = False):
    """Retrieve triggered alert logs with AI contextual explanations and impact levels."""
    return alert_engine_service.get_alerts(unread_only=unread_only)

@router.post("/{alert_id}/read")
async def mark_alert_read(alert_id: str):
    """Mark a notification as read."""
    success = alert_engine_service.mark_as_read(alert_id)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "success", "alert_id": alert_id}

@router.get("/rules", response_model=List[AlertRuleItem])
async def get_alert_rules():
    """List configured threshold and event alert rules."""
    return alert_engine_service.get_rules()

@router.post("/rules", response_model=AlertRuleItem)
async def create_alert_rule(payload: CreateRulePayload):
    """Configure a new real-time alert trigger rule."""
    return alert_engine_service.add_rule(
        symbol=payload.symbol,
        category=payload.category,
        condition_type=payload.condition_type,
        threshold=payload.threshold_value
    )
