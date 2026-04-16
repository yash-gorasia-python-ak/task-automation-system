from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class RequestMetadata(Base):
    __tablename__ = "request_metadata"

    request_id: Mapped[str] = mapped_column(String(50), primary_key=True, index=True)
    method: Mapped[str] = mapped_column(String(10), nullable=False)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    status_code: Mapped[str] = mapped_column(String(5), nullable=False)
    response_time: Mapped[str] = mapped_column(Text, nullable=False)
