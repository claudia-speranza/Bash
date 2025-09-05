from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Float, ColumnElement
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column


class Base(DeclarativeBase):
    pass

class OperationBase(Base):
    """Base class with common timestamp fields."""
    __abstract__ = True
    data_operazione: Mapped[DateTime] = mapped_column(DateTime, nullable=False, index=True, primary_key=True)
    data_valuta: Mapped[Optional[DateTime]] = mapped_column(DateTime)
    importo: Mapped[float] = mapped_column(Float, default=0, primary_key=True)
    descrizione: Mapped[Optional[str]] = mapped_column(String)

    @classmethod
    def in_timerange(cls, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None):
        start_date = start_date or datetime.min
        end_date = end_date or datetime.now()

        return cls.data_operazione.between(start_date, end_date)

    @classmethod
    def is_entrata(cls) -> ColumnElement[bool]:
        """Check if the movement is an entry (positive amount)."""
        return cls.importo > 0

    @classmethod
    def is_uscita(cls) -> ColumnElement[bool]:
        """Check if the movement is an exit (negative amount)."""
        return cls.importo < 0







