from fastapi import APIRouter
from typing import List
from backend.app.services.ai.forecasting import ai_forecasting_service, LearningLesson

router = APIRouter(prefix="/learning", tags=["Investment Learning & Education"])

@router.get("/lessons", response_model=List[LearningLesson])
async def get_lessons():
    """Retrieve structured educational lessons based on Buffett principles, risk management, and behavioral finance."""
    return ai_forecasting_service.get_learning_lessons()
