from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timezone

from database import get_db
from models import User, Event, Fight, Pick
from schemas import UserCreate, UserLogin, Token, EventCreate, FightCreate, PickCreate
from auth import hash_password, verify_password, create_access_token, get_current_user

app = FastAPI()

@app.post("/register", response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already has been registered")

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    access_token = create_access_token({"sub": new_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if db_user is None or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password has been given")

    access_token = create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "id": current_user.id}

@app.post("/events")
def create_event(event: EventCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_event = Event(name=event.name, lock_time=event.lock_time)
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

@app.post("/fights")
def create_fight(fight: FightCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    event = db.query(Event).filter(Event.id == fight.event_id).first()
    if event is None:
        raise HTTPException(status_code=404, detail="Event has not been found")

    new_fight = Fight(
        event_id=fight.event_id,
        fighter_a=fight.fighter_a,
        fighter_b=fight.fighter_b,
    )
    db.add(new_fight)
    db.commit()
    db.refresh(new_fight)
    return new_fight

@app.post("/picks")
def submit_pick(pick: PickCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fight = db.query(Fight).filter(Fight.id == pick.fight_id).first()
    if fight is None:
        raise HTTPException(status_code=404, detail="Fight has not been found")

    if datetime.now(timezone.utc) >= fight.event.lock_time:
        raise HTTPException(status_code=403, detail="Picks are now locked for this event")

    new_pick = Pick(
        user_id=current_user.id,
        fight_id=pick.fight_id,
        picked_winner=pick.picked_winner,
    )
    db.add(new_pick)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="You have already picked for this fight")

    db.refresh(new_pick)
    return new_pick


    