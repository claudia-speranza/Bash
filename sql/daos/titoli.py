from typing import Optional

import pandas as pd
from sqlalchemy import select, func, case
from sqlalchemy.orm import selectinload

from sql.daos.basic import BasicDao
from sql.models.titoli import TitoliModel
from sql.utils import logger


class Titoli(BasicDao):
    """Class for handling titoli data."""
    def __init__(self):
        super().__init__(TitoliModel)

    def get_by_isin(self, isin: str) -> Optional[TitoliModel]:
        """Filter by ISIN."""
        try:
            stmt = (select(TitoliModel)
                    .options(selectinload(TitoliModel.ordini))
                    .where(TitoliModel.isin == isin))
            return self.get_one(stmt)
        except Exception as e:
            logger.error(f'Failed to load titolo with isin {isin} due to exception: {e}')
        return None

    def get_etfs(self) -> pd.DataFrame:

        stmt = (select(TitoliModel)
                .options(selectinload(TitoliModel.ordini))
                .where(TitoliModel.strumento == 'ETF'))

        return self.get_all(stmt, as_dataframe=True)

if __name__ == '__main__':
    result = Titoli().get_with_quantity()
    print(result)


