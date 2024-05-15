from sqlalchemy import BigInteger, Column, String

from app.store.database.sqlalchemy_base import BaseModel


class AdminModel(BaseModel):
    __tablename__ = "admins"

    id = Column(BigInteger, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
