from sqlmodel import Session, select
from fastapi import APIRouter
from dundie.db import ActiveSession
from dundie.models.user import User, UserResponse, UserRequest
from typing import List


router = APIRouter()

@router.get("/")
async def list_users(*, session: Session = ActiveSession) -> List[UserResponse]:
    """List all users from database."""
    users = session.exec(select(User)).all()
    return users

@router.get("/{username}/")
async def get_user_by_username(*, username: str, session: Session = ActiveSession) -> UserResponse:
    """Get a user by username."""
    user = session.exec(select(User).where(User.username == username)).first()
    return user


@router.post("/", status_code=201)
async def create_user(*, user: UserRequest, session: Session = ActiveSession) -> UserResponse:
    """Create a new user."""
    user = User.from_orm(user)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user