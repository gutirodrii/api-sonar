from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional
from datetime import datetime
import random
from pydantic import BaseModel

from database import engine, get_session
from models import User, Throw, FirstThrow, Screen, SQLModel, Pulsera

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# Request Models
class UserCreate(BaseModel):
    id: int
    group_id: Optional[int] = None
    thrower: Optional[int] = None


class StateUpdate(BaseModel):
    state: int


class ScreenUpdate(BaseModel):
    screen_name: str  # "screen1", "screen2", "screen3"


class ClaimFirstThrow(BaseModel):
    claimed_value: int


# Endpoints


@app.post("/users/", response_model=User)
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    # Verify Pulsera ID exists
    pulsera = session.get(Pulsera, user_data.id)
    if not pulsera:
        raise HTTPException(status_code=400, detail="Pulsera ID does not exist")

    # Check if user already exists
    if session.get(User, user_data.id):
        raise HTTPException(status_code=400, detail="User with this ID already exists")

    # Create User
    new_user = User(
        id=user_data.id, state=0, group_id=user_data.group_id, thrower=user_data.thrower
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    # Create associated Screen record
    new_screen = Screen(user_id=new_user.id)
    session.add(new_screen)
    session.commit()

    return new_user


# Create
@app.get("/users/{user_id}/state")
def get_state(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.state


@app.patch("/users/{user_id}/state")
def update_state(
    user_id: int, state_data: StateUpdate, session: Session = Depends(get_session)
):
    if state_data.state not in [0, 1, 2]:
        raise HTTPException(status_code=400, detail="State must be 0, 1, or 2")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.state = state_data.state
    session.add(user)
    session.commit()
    return {"ok": True}


@app.post("/users/{user_id}/screens")
def update_screen(
    user_id: int, update: ScreenUpdate, session: Session = Depends(get_session)
):
    screen_record = session.get(Screen, user_id)
    if not screen_record:
        # Fallback if for some reason it wasn't created, or user doesn't exist
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        screen_record = Screen(user_id=user_id)

    now = datetime.utcnow()
    if update.screen_name == "screen1":
        screen_record.screen1 = now
    elif update.screen_name == "screen2":
        screen_record.screen2 = now
    elif update.screen_name == "screen3":
        screen_record.screen3 = now
    else:
        raise HTTPException(status_code=400, detail="Invalid screen name")

    session.add(screen_record)
    session.commit()
    return {"ok": True}


@app.post("/users/{user_id}/throw", response_model=Throw)
def throw_dice(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    value = random.randint(1, 6)
    new_throw = Throw(user_id=user_id, value=value)
    session.add(new_throw)
    session.commit()
    session.refresh(new_throw)
    return new_throw


@app.post("/users/{user_id}/claim-first", response_model=FirstThrow)
def claim_first_throw(
    user_id: int, claim: ClaimFirstThrow, session: Session = Depends(get_session)
):
    # Check if already claimed
    existing = session.exec(
        select(FirstThrow).where(FirstThrow.user_id == user_id)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="First throw already claimed")

    # Find the first throw for this user
    # We need to order by time
    statement = select(Throw).where(Throw.user_id == user_id).order_by(Throw.throw_time)
    first_throw_record = session.exec(statement).first()

    if not first_throw_record:
        raise HTTPException(status_code=400, detail="No throws recorded for this user")

    new_claim = FirstThrow(
        id=first_throw_record.id,  # Use the same ID as the throw
        user_id=user_id,
        true_value=first_throw_record.value,
        claimed_value=claim.claimed_value,
    )
    session.add(new_claim)

    # Update User with first_throw_id
    user = session.get(User, user_id)
    if user:
        user.first_throw_id = first_throw_record.id
        session.add(user)

    session.commit()
    session.refresh(new_claim)
    return new_claim
