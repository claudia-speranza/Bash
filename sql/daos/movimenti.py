from datetime import datetime
from typing import Optional

import pandas as pd
from sqlalchemy import select, func, and_

from sql.daos.basic import BasicTimedDao
from sql.models.movimenti import MovimentiModel, MovimentiCategory


class Movimenti(BasicTimedDao):
    """Class for handling banking movements data."""

    def __init__(self):
        super().__init__(MovimentiModel)

    def get_liquidita(self, start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> float:
        """Calculate total liquidity (sum of entrate_uscite)."""
        stmt = (
            select(func.sum(MovimentiModel.importo))
            .where(MovimentiModel.in_timerange(start_date, end_date))
        )
        # Calculate total from the filtered results
        total = self.get_one(stmt)
        return round(total, 2) if total else 0.0

    def sum_by_category(self, category: MovimentiCategory, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> float:
        """Calculate total investments positive value."""
        stmt = (
            select(func.sum(MovimentiModel.importo))
            .where(and_(MovimentiModel.in_timerange(start_date, end_date),
                        MovimentiModel.is_category(category)))
        )
        # Calculate total from the filtered results
        total = self.get_one(stmt)
        return round(total, 2) if total else 0.0

    def get_by_category(self, category: MovimentiCategory, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Filter movements by category."""
        stmt = (
            select(MovimentiModel)
            .where(and_(MovimentiModel.in_timerange(start_date, end_date),
                        MovimentiModel.is_category(category)))
            .order_by(MovimentiModel.data_operazione)
        )
        return self.get_all(stmt, as_dataframe=True)

    def get_by_description(self, description: str, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Get account stamp duty taxes."""
        stmt = (
            select(MovimentiModel)
            .where(and_(MovimentiModel.in_timerange(start_date, end_date),
                        MovimentiModel.descrizione == description))
        )
        return self.get_all(stmt, as_dataframe=True)



if __name__ == "__main__":
    movimenti_dao = Movimenti()
    # start_date = datetime(2025, 1, 1)
    # end_date = datetime(2025, 12, 31)
    # print(movimenti_dao.get_liquidita() )
    df = movimenti_dao.get_by_category(MovimentiCategory('Bonifici'))
    print(df)
