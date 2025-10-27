"""User related data models."""
from typing import Optional
from sqlmodel import Field, SQLModel
from dundie.security import HashedPassword



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
