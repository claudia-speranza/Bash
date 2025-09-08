from enum import Enum

from sqlalchemy import String, func, ColumnElement, or_
from sqlalchemy.orm import Mapped, mapped_column

from sql.models.basic import OperationBase


class MovimentiCategory(Enum):
    """Enumeration for movement categories."""
    CompravenditaTitoli = "CompravenditaTitoli"
    SpeseConto = "SpeseConto"
    Bonifici = "Bonifici"
    Commissioni = "Commissioni"
    Tasse = "Tasse"
    Dividendi = "Dividendi"
    AltriMovimenti = "AltriMovimenti"
    Interessi = "Interessi"

    def __str__(self):
        return self.value

    @classmethod
    def list_values(cls):
        return [category.value for category in cls]

category_map = {
    MovimentiCategory.Bonifici: ['bonifico'],
    MovimentiCategory.CompravenditaTitoli: ['compravendita titoli', 'rimborso titoli'],
    MovimentiCategory.Tasse: ['imposta', 'riten'],
    MovimentiCategory.Dividendi: ['stacco cedole', 'dividendo'],
    MovimentiCategory.Interessi: ['interessi'],
    MovimentiCategory.SpeseConto: ['canone mensile'],
}

class MovimentiModel(OperationBase):
    """SQLAlchemy model for the movimenti table."""
    __tablename__ = 'movimenti'

    descrizione_completa: Mapped[str] = mapped_column(String, primary_key=True)

    def __repr__(self):
        return f"<Movimento(data='{self.data_operazione}', importo={self.importo}, descrizione={self.descrizione})>"

    @classmethod
    def is_category(cls, category: MovimentiCategory) -> ColumnElement[bool]:
        """Filter by movement category."""
        if category == MovimentiCategory.AltriMovimenti:
            return ~or_(
                cls.is_category(MovimentiCategory.Bonifici),
                cls.is_category(MovimentiCategory.CompravenditaTitoli),
                cls.is_category(MovimentiCategory.Tasse),
                cls.is_category(MovimentiCategory.Dividendi),
                cls.is_category(MovimentiCategory.Interessi),
                cls.is_category(MovimentiCategory.SpeseConto),
            )
        keywords = category_map.get(category, [])
        if not keywords:
            return False

        conditions = [func.lower(cls.descrizione).like(f'%{kw}%') for kw in keywords]
        return or_(*conditions)
