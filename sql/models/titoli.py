from typing import Optional, List

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sql.models.basic import Base
from sql.models.ordini import OrdiniModel


class TitoliModel(Base):
    """SQLAlchemy model for the movimenti table."""
    __tablename__ = 'titoli'

    isin: Mapped[str] = mapped_column(String, ForeignKey("titoli.isin"), nullable=False, index=True, primary_key=True)
    titolo: Mapped[Optional[str]] = mapped_column(String)
    simbolo: Mapped[Optional[str]] = mapped_column(String)
    mercato: Mapped[Optional[str]] = mapped_column(String)
    strumento: Mapped[Optional[str]] = mapped_column(String)
    valuta: Mapped[Optional[str]] = mapped_column(String)

    # Relationship to orders
    ordini: Mapped[List[OrdiniModel]] = relationship(
        "OrdiniModel",
        back_populates="titolo_info",
    )

    def __repr__(self):
        return f"<Titolo(isin={self.isin}, titolo='{self.titolo}'>"