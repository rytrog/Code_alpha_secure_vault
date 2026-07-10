from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..database.schemas import ChatRequest, ExplainRequest
from ..database.models import User
from ..database import crud
from ..dependencies import require_admin
from ..services.ai_service import explain_attack_log, generate_report, get_ai_recommendations, chat
from ..utils.response import success_response

router = APIRouter(prefix="/api/ai", tags=["AI"])


@router.post("/explain")
async def explain_attack(data: ExplainRequest, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    result = await explain_attack_log(db, data.attack_log_id)
    return success_response(result, "AI explanation generated")


@router.post("/report")
async def generate_ai_report(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    result = await generate_report(db, current_user.username)
    return success_response(result, "AI report generated")


@router.get("/recommendations")
async def recommendations(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    result = await get_ai_recommendations(db)
    return success_response(result, "Recommendations generated")


@router.post("/chat")
async def ai_chat(data: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    reply = await chat(db, current_user.id, data.message)
    return success_response({"reply": reply})


@router.get("/chat/history")
def chat_history(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    messages = crud.get_chat_history(db, current_user.id)
    return success_response([{
        "role": m.role, "content": m.content, "timestamp": str(m.timestamp)
    } for m in reversed(messages)])


@router.delete("/chat/clear")
def clear_chat(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    crud.clear_chat_history(db, current_user.id)
    return success_response(message="Chat history cleared")
