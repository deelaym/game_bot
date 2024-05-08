from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import BaseModel

UserSession = Table(
    "user_session",
    BaseModel.metadata,
    Column("id", BigInteger, primary_key=True),
    Column("user_id", BigInteger, ForeignKey("users.id_")),
    Column("session_id", BigInteger, ForeignKey("sessions.id_")),
    Column("points", Integer, default=0),
    Column("in_game", Boolean, default=True),
    Index("user_id_session_id", "user_id", "session_id", unique=True),
)


class UserModel(BaseModel):
    __tablename__ = "users"

    id_ = Column(BigInteger, primary_key=True)
    first_name = Column(String, nullable=False)
    username = Column(String)
    sessions = relationship(
        "SessionModel",
        secondary=UserSession,
        back_populates="users",
        lazy="joined",
    )


class SessionModel(BaseModel):
    __tablename__ = "sessions"

    id_ = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)
    in_progress = Column(Boolean, default=True)
    round_number = Column(Integer, default=1)
    users = relationship(
        "UserModel",
        secondary=UserSession,
        back_populates="sessions",
        lazy="joined",
    )
