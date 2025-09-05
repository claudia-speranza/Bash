from typing import Optional

from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sql.models.basic import OperationBase


class OrdiniModel(OperationBase):
    """SQLAlchemy model for the ordini table."""
    __tablename__ = 'ordini'

    isin: Mapped[str] = mapped_column(String, ForeignKey("titoli.isin"), nullable=False, index=True, primary_key=True)
    segno: Mapped[Optional[str]] = mapped_column(String)
    quantita: Mapped[Optional[float]] = mapped_column(Float)
    divisa: Mapped[Optional[str]] = mapped_column(String)
    prezzo: Mapped[Optional[float]] = mapped_column(Float)
    cambio: Mapped[Optional[float]] = mapped_column(Float)
    controvalore: Mapped[float] = mapped_column(Float, primary_key=True)
    commissione: Mapped[float] = mapped_column(Float, default=0)
    tipo_commissione: Mapped[Optional[str]] = mapped_column(String)
    importo: Mapped[float] = mapped_column(Float, default=0, primary_key=True)

    # Relationship to titolo
    titolo_info: Mapped["TitoliModel"] = relationship(
        "TitoliModel",
        back_populates="ordini"
    )

    def __repr__(self):
        return f"<Ordine(data='{self.data_operazione}', isin='{self.isin}', quantita={self.quantita}, prezzo={self.prezzo})>"