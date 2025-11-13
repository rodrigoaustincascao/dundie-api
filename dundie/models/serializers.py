from datetime import datetime
from logging import root
from typing import Optional
from pydantic import BaseModel, root_validator
from dundie.db import engine
from sqlmodel import Session
from dundie.models.user import User


class TransactionResponse(BaseModel):
    id: int
    value: int
    date: datetime
    user: Optional[str] = None
    from_user: Optional[str] = None

    @root_validator(pre=True)
    def get_usernames(cls, values):
        with Session(engine) as session:
            user = session.get(User, values["user_id"])
            from_user = session.get(User, values["from_id"])
            values["user"] = user and user.username
            values["from_user"] = from_user and from_user.username
        return values
      