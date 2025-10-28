"""User related data models."""
from typing import Optional
from sqlmodel import Field, SQLModel
from dundie.security import HashedPassword
from pydantic import BaseModel, root_validator


class User(SQLModel, table=True):
    """Represents the User in the system."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    username: str = Field(unique=True, nullable=False)
    avatar: Optional[str] = None
    bio: Optional[str] = None
    password: HashedPassword
    name: str = Field(nullable=False)
    dept: str = Field(nullable=False)
    currency: str = Field(nullable=False)

    @property
    def superuser(self):
        """Users belonging to management dept are admins."""
        return self.dept == "management"
    
def generate_username(name: str) -> str:
    """Generate a slug from user.name"""
    return name.lower().replace(" ", "-").replace("_", "-")

class UserResponse(BaseModel):
    """Serializer for when we send a response to the client."""

    username: str
    name: str
    dept: str
    avatar: Optional[str] = None
    bio: Optional[str] = None
    currency: str

class UserRequest(BaseModel):
    """Serializer for User request payload"""

    name: str
    email: str
    dept: str
    password: str
    currency: str = "USD"
    username: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None

    @root_validator(pre=True)
    def generate_username_if_not_set(cls, values):
        """Generates username if not set"""
        if values.get("username") is None:
            values["username"] = generate_username(values["name"])
        return values