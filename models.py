from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True)
    state: int = Field(description="State must be 0, 1, or 2")
    group_id: Optional[int] = None
    thrower: Optional[int] = None
    first_throw_id: Optional[int] = None


class Throw(SQLModel, table=True):
    __tablename__ = "throws"
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    value: int
    throw_time: datetime = Field(default_factory=datetime.utcnow)


class FirstThrow(SQLModel, table=True):
    __tablename__ = "firstthrow"
    id: Optional[int] = Field(
        default=None, primary_key=True
    )  # This will be the same as throw.id
    user_id: int = Field(foreign_key="users.id")
    true_value: int
    claimed_value: int


class Screen(SQLModel, table=True):
    __tablename__ = "screens"
    user_id: int = Field(foreign_key="users.id", primary_key=True)
    screen1: Optional[datetime] = None
    screen2: Optional[datetime] = None
    screen3: Optional[datetime] = None


class Pulsera(SQLModel, table=True):
    __tablename__ = "pulsera"
    id: str = Field(
        primary_key=True,
        description="ID de la pulsera, hexadecimal de 8 caracteres",
    )
