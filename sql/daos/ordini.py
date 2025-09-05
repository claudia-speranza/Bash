from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, func, and_, asc, text

from sql.daos.basic import BasicTimedDao
from sql.models.ordini import OrdiniModel


class Ordini(BasicTimedDao):
    """Class for handling orders data."""

    def __init__(self):
        super().__init__(OrdiniModel)

    def get_investimenti_correnti(self, start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> float:
        """Calculate total investments positive value."""
        stmt = (
            select(func.sum(OrdiniModel.importo))
            .where(OrdiniModel.in_timerange(start_date, end_date))
        )
        # Calculate total from the filtered results
        total = self.get_one(stmt)
        return - round(total, 2) if total else 0.0

    def filter_by_isin(self, isin: str) -> List[OrdiniModel]:
        """Filter orders by ISIN."""
        stmt = (
            select(func.sum(OrdiniModel.importo))
            .where(OrdiniModel.isin == isin)
        )
        return self.get_all(stmt)


if __name__ == "__main__":
    Ordini()