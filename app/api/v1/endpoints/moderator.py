from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/{post_id}/decision/{decision}")
async def set_decision(post_id: int, decision: str):
    # TODO: Implement decision logic
    return {"message": "Decision set successfully"} 