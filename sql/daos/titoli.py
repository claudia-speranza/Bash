from typing import Optional, Union, List

import pandas as pd
from sqlalchemy import select, func, case, or_, outerjoin, and_, desc
from sqlalchemy.orm import selectinload

from sql.daos.basic import BasicDao
from sql.daos.ordini import analyze_orders
from sql.models.ordini import OrdiniModel
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

    def get_with_quantity(self):
        stmt = (select(TitoliModel.isin, TitoliModel.titolo, TitoliModel.strumento,
                       func.coalesce(func.sum(
                           case((OrdiniModel.importo >= 0, -OrdiniModel.quantita),
                                else_=OrdiniModel.quantita)), 0).label('portfolio_quantity'),
                       func.coalesce(func.sum(OrdiniModel.controvalore), 0).label('portfolio_value'))
                .outerjoin(OrdiniModel, and_(TitoliModel.isin == OrdiniModel.isin, OrdiniModel.prezzo != 0))
                .group_by(TitoliModel.isin).order_by(TitoliModel.strumento, desc('portfolio_value'))
                )
        return self.get_all(stmt, True)

    def get_full_info(self) -> pd.DataFrame:
        stmt = (select(TitoliModel)
                .options(selectinload(TitoliModel.ordini))
                .order_by(TitoliModel.strumento, TitoliModel.titolo))
        titoli_full = self.get_all(stmt, False)
        titoli_info = [dict(isin=titolo.isin,
                            titolo=titolo.titolo,
                            strumento=titolo.strumento,
                            **analyze_orders(titolo.ordini, titolo.strumento)) for titolo in titoli_full]
        return pd.DataFrame(titoli_info)

    def get_azioni(self, as_dataframe: bool = False) -> Union[List[TitoliModel], pd.DataFrame]:

        stmt = (select(TitoliModel)
                .where(or_(TitoliModel.strumento == 'ETF', TitoliModel.strumento == 'Azione')))

        return self.get_all(stmt, as_dataframe)

    def get_obbligazioni(self, as_dataframe: bool = False) -> Union[List[TitoliModel], pd.DataFrame]:

        stmt = (select(TitoliModel)
                .where(TitoliModel.strumento == 'Obbligazione'))

        return self.get_all(stmt, as_dataframe)
#
# if __name__ == '__main__':
#     result = Titoli().get_full_info()
#     print(result)


