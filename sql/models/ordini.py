from sqlalchemy import Column, Integer, String, Float, DateTime

from sql.models.basic import Base


class OrdiniModel(Base):
    """SQLAlchemy model for the ordini table."""
    __tablename__ = 'ordini'

    data_operazione = Column(DateTime, nullable=False, index=True, primary_key=True)
    data_valuta = Column(DateTime)
    isin = Column(String, nullable=False, index=True, primary_key=True)
    descrizione = Column(String)
    segno = Column(Integer)  # 1 for 'A', -1 for 'V', 0 for 'other'
    quantita = Column(Float)
    divisa = Column(String)
    prezzo = Column(Float)
    cambio = Column(Float)
    controvalore = Column(Float, primary_key=True)
    commissioni_fondi_sw = Column(Float, default=0)
    commissioni_fondi_banca = Column(Float, default=0)
    spese_fondi_sgr = Column(Float, default=0)
    commissioni_amministrato = Column(Float, default=0)

    def __repr__(self):
        return f"<Ordine(data='{self.data_operazione}', isin='{self.isin}', quantita={self.quantita}, prezzo={self.prezzo})>"

    @property
    def spese_totali(self) -> float:
        return (self.commissioni_fondi_sw + self.commissioni_fondi_banca +
                self.spese_fondi_sgr + self.commissioni_amministrato)