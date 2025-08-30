from sqlalchemy import Column, DateTime, String, Float

from sql.models.basic import Base


class MovimentiModel(Base):
    """SQLAlchemy model for the movimenti table."""
    __tablename__ = 'movimenti'

    data_operazione = Column(DateTime, nullable=False, index=True, primary_key=True)
    data_valuta = Column(DateTime, nullable=False)
    descrizione = Column(String)
    descrizione_completa = Column(String, primary_key=True)
    importo = Column(Float, default=0, primary_key=True)

    def __repr__(self):
        return f"<Movimento(data='{self.data_operazione}', importo={self.importo}, descrizione={self.descrizione})>"

    @property
    def entrate(self) -> float:
        """Return positive amounts (entrate)."""
        return self.importo if self.importo > 0 else 0.0

    @property
    def uscite(self) -> float:
        """Return negative amounts as positive (uscite)."""
        return -self.importo if self.importo < 0 else 0.0