from sqlalchemy import Column, String

from sql.models.basic import Base


class TitoliModel(Base):
    """SQLAlchemy model for the movimenti table."""
    __tablename__ = 'titoli'

    isin = Column(String, nullable=False, index=True, primary_key=True)
    titolo = Column(String)
    simbolo = Column(String)
    mercato = Column(String)
    strumento = Column(String)
    valuta = Column(String)

    def __repr__(self):
        return f"<Titolo(isin={self.isin}, titolo='{self.titolo}'>"

    @property
    def table_name(self) -> str:
        return self.__tablename__