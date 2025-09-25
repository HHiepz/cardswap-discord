from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base
from database.base import Base
import datetime


class HistoryExchangeCard(Base):
    __tablename__ = "history_exchange_cards"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Người dùng khai báo
    telco: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[int] = mapped_column(Integer, default=0)
    code: Mapped[str] = mapped_column(String(255), nullable=False)
    serial: Mapped[str] = mapped_column(String(255), nullable=False)
    # Hệ thống xử lý
    user_discord_id: Mapped[str] = mapped_column(String(255), nullable=False)
    message_discord_id: Mapped[str] = mapped_column(String(255), nullable=False)
    channel_discord_id: Mapped[str] = mapped_column(String(255), nullable=True)
    card_value: Mapped[int] = mapped_column(Integer, default=0)
    server: Mapped[str] = mapped_column(String(255), nullable=True)
    request_id: Mapped[str] = mapped_column(String(255), nullable=False)
    transaction_id: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(
        Enum("success", "failed", "wrong_amount", "pending"),
        nullable=False,
        default="pending",
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.datetime.utcnow,
        onupdate=datetime.datetime.utcnow,
    )
