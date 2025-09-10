from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from database.base import Base
import datetime


class Card2k(Base):
    __tablename__ = "card2k"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    partner_id: Mapped[str] = mapped_column(String(255), nullable=False)
    partner_key: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
