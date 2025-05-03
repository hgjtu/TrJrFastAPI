from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(
    prefix="/admins",
    tags=["Администраторы"],
    responses={404: {"description": "Not found"}},
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/{username}/set-moderator")
async def set_moderator(username: str):
    # TODO: Implement set moderator logic
    return {"message": "Moderator role set successfully"} 