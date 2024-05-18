from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from app.store.database.sqlalchemy_base import BaseModel


class UserSession(BaseModel):
    __tablename__ = "user_session"

    id_ = Column(BigInteger, primary_key=True)
    user_id = Column(BigInteger, ForeignKey("users.id_"))
    session_id = Column(BigInteger, ForeignKey("sessions.id_"))
    points = Column(Integer, default=0)
    in_game = Column(Boolean, default=True)
    file_id = Column(String)
    __table_args__ = (
        Index("user_id_session_id", "user_id", "session_id", unique=True),
    )


class UserModel(BaseModel):
    __tablename__ = "users"

    id_ = Column(BigInteger, primary_key=True)
    first_name = Column(String, nullable=False)
    username = Column(String)
    sessions = relationship(
        "SessionModel",
        secondary="user_session",
        back_populates="users",
    )

    @property
    def display_name(self) -> str:
        return f"@{self.username}" if self.username else self.first_name


class SessionModel(BaseModel):
    __tablename__ = "sessions"

    id_ = Column(BigInteger, primary_key=True)
    chat_id = Column(BigInteger, nullable=False)
    in_progress = Column(Boolean, default=True)
    round_number = Column(Integer, default=1)
    state = Column(String, default="start")
    message_id = Column(BigInteger)
    polls_time = Column(Integer, default=60)
    users = relationship(
        "UserModel",
        secondary="user_session",
        back_populates="sessions",
        lazy="joined",
    )
