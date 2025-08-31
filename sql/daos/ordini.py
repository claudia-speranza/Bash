from datetime import datetime
from typing import List, Optional

from sql.daos.basic import BasicTimedDao
from sql.models.ordini import OrdiniModel


class Ordini(BasicTimedDao):
    """Class for handling orders data."""

    def __init__(self):
        super().__init__(OrdiniModel)

    def get_investimenti(self, start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> float:
        """Calculate total investments."""
        filtered_orders = self.get_in_timerange(start_date, end_date)

        # Calculate total from the filtered results
        total = sum(order.totale for order in filtered_orders if order.totale is not None)
        return total

    def filter_by_isin(self, isin: str) -> List[OrdiniModel]:
        """Filter orders by ISIN."""
        with self.db_manager.get_session() as session:
            query = session.query(OrdiniModel).filter(OrdiniModel.isin == isin)
            return query.all()