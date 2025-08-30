from typing import List

from sql.daos.basic import BasicDao
from sql.models.titoli import TitoliModel


class Titoli(BasicDao):
    """Class for handling titoli data."""
    def __init__(self):
        super().__init__(TitoliModel)

    def filter_by_isin(self, isin: str) -> List[TitoliModel]:
        """Filter orders by ISIN."""
        with self.db.session() as session:
            query = session.query(TitoliModel).filter(TitoliModel.isin == isin)
            return query.all()

