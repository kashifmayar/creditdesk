from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.policy import PolicyAskRequest, PolicyAskResponse, PolicyStatusResponse
from app.services.rag_service import answer_policy_question, get_policy_status

router = APIRouter()


@router.get("/status", response_model=PolicyStatusResponse)
async def policy_status(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return PolicyStatusResponse(**await get_policy_status(db))


@router.post("/ask", response_model=PolicyAskResponse)
async def ask_policy(
    req: PolicyAskRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    try:
        result = await answer_policy_question(req.question, db)
        return PolicyAskResponse(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Policy Q&A failed: {e}")
