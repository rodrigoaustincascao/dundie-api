from sqlmodel import Session, select
from fastapi import APIRouter, HTTPException, Body, BackgroundTasks
from dundie.db import ActiveSession
from dundie.models.user import (
    User, 
    UserResponse, 
    UserRequest, 
    UserProfilePatchReuest, 
    UserPasswordPatchRequest,
    UserResponseWithBalance,
)
from typing import List
from dundie.auth import AuthenticatedUser, SuperUser, CanChangeUserPassword
from sqlalchemy.exc import IntegrityError
from dundie.tasks.user import try_to_send_pwd_reset_email
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import parse_obj_as
from dundie.auth import ShowBalanceField



router = APIRouter()

@router.get("/",
            dependencies=[AuthenticatedUser],
            response_model_exclude_unset=True # Omite os campos virtuais
            )
async def list_users(
    *,
    session: Session = ActiveSession,
    show_balance_field: bool = ShowBalanceField
    
    ) -> List[UserResponse] | List[UserResponseWithBalance]:
    """List all users from database."""
    users = session.exec(select(User)).all()
    if show_balance_field:
        users_with_balance = parse_obj_as(List[UserResponseWithBalance], users)
        return JSONResponse(jsonable_encoder(users_with_balance))
    return users

@router.get("/{username}/")
async def get_user_by_username(*, username: str, session: Session = ActiveSession) -> UserResponse:
    """Get a user by username."""
    user = session.exec(select(User).where(User.username == username)).first()
    return user


@router.post(
    "/", response_model=UserResponse, status_code=201, dependencies=[SuperUser]
)
async def create_user(*, session: Session = ActiveSession, user: UserRequest):
    """Creates new user"""
    # LBYL
    if session.exec(select(User).where(User.username == user.username)).first():
        raise HTTPException(status_code=409, detail="Username already taken")

    db_user = User.from_orm(user)  # transform UserRequest in User
    session.add(db_user)
    # EAFP
    try:
        session.commit()
    except IntegrityError:
        raise HTTPException(status_code=500, detail="Database IntegrityError")

    session.refresh(db_user)
    return db_user

@router.patch("/{username}/")
async def update_user(
    *,
    session: Session = ActiveSession,
    patch_data: UserProfilePatchReuest,
    current_user: User = AuthenticatedUser,
    username: str) -> UserResponse:

    user = session.exec(select(User).where(User.username == username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id != current_user.id and not current_user.superuser:
        raise HTTPException(
            status_code=403, 
            detail="You can only update your own profiel"
            )
    
    # Update
    user.avatar = patch_data.avatar if patch_data.avatar is not None else user.avatar
    user.bio = patch_data.bio if patch_data.bio is not None else user.bio
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/{username}/password/", response_model=UserResponse)
async def change_password(
    *,
    session: Session = ActiveSession,
    patch_data: UserPasswordPatchRequest,
    user: User = CanChangeUserPassword
):
    user.password = patch_data.hashed_password  # pyright: ignore
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.post("/pwd_reset_token/")
async def send_password_reset_token(
        *, 
        email: str = Body(embed=True),
        background_tasks: BackgroundTasks
    
    ):
    """Sends an email with the token to reset password."""
    background_tasks.add_task(try_to_send_pwd_reset_email, email=email)
    return {
        "message": "If we found a user with that email, we sent a password reset token to it."
    }