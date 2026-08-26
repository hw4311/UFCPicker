from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    picks = relationship("Pick", back_populates="user")

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    lock_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    fights = relationship("Fight", back_populates="event")

class Fight(Base):
    __tablename__ = "fights"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    fighter_a = Column(String, nullable=False)
    fighter_b = Column(String, nullable=False)
    winner = Column(String, nullable=True)

    event = relationship("Event", back_populates="fights")
    picks = relationship("Pick", back_populates="fight")

class Pick(Base):
    __tablename__ = "picks"
    __table_args__ = (
        UniqueConstraint("user_id", "fight_id", name="unique_user_fight_pick"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fight_id = Column(Integer, ForeignKey("fights.id"), nullable=False)
    picked_winner = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="picks")
    fight = relationship("Fight", back_populates="picks")

    
