from fastapi import FastAPI
from dundie.models.user import UserResponse
from dundie.db import ActiveSession
from sqlmodel import Session, select
from dundie.models import User
from dundie.routes import main_router




app = FastAPI(
    title="dundie",
    version="0.1.0",
    description="dundie is a rewards API"
)

app.include_router(main_router)

