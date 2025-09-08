from datetime import datetime
from typing import List, Dict, Any, Optional

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

    def get_investimenti(self, start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> float:
        """Calculate total investments positive value."""
        stmt = (
            select(func.sum(MovimentiModel.importo))
            .where(and_(MovimentiModel.in_timerange(start_date, end_date),
                        MovimentiModel.is_category(MovimentiCategory.CompravenditaTitoli)))
        )
        # Calculate total from the filtered results
        total = self.get_one(stmt)
        return - round(total, 2) if total else 0.0

    def get_versamenti(self, start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> float:
        """Calculate total liquidity (sum of entrate_uscite)."""
        stmt = (
            select(func.sum(MovimentiModel.importo))
            .where(MovimentiModel.in_timerange(start_date, end_date))
        )
        # Calculate total from the filtered results
        total = self.get_one(stmt)
        return round(total, 2) if total else 0.0

    def get_imposte_di_bollo(self) -> List[Dict[str, Any]]:
        """Get account stamp duty taxes."""
        stmt = (
            select(MovimentiModel)
            .where(MovimentiModel.descrizione == 'Imposta bollo conto corrente')
        )
        # Calculate total from the filtered results
        result_df = self.get_all(stmt, as_dataframe=True)

        result_df['data'] = (
            result_df['descrizione_completa']
            .str.extract(r'(\d{2}\.\d{2}\.\d{4})', expand=False)
            .pipe(lambda x: pd.to_datetime(x, format='%d.%m.%Y', errors='coerce'))
        )
        result_df['importo'] = -result_df['importo']
        result_df = result_df[['data', 'importo' ]]
        return result_df

    def get_imposte_dossier(self) -> List[Dict[str, Any]]:
        """Get dossier stamp duty taxes."""

        def extract_dossier(descrizione_completa):
            if pd.isna(descrizione_completa) or not descrizione_completa:
                return None
            parts = descrizione_completa.split(' ')
            return parts[-1] if parts else None

        stmt = (
            select(MovimentiModel)
            .where(MovimentiModel.descrizione == 'Imposta bollo dossier titoli')
        )
        # Calculate total from the filtered results
        result_df = self.get_all(stmt, as_dataframe=True)
        result_df['dossier'] = result_df['descrizione_completa'].apply(extract_dossier)
        result_df['importo'] = -result_df['importo']
        result_df = result_df[['data_operazione', 'importo', 'dossier']]
        return result_df

    def get_by_category(self, category: MovimentiCategory) -> pd.DataFrame:
        """Filter movements by category."""
        stmt = (
            select(MovimentiModel)
            .where(MovimentiModel.is_category(category))
            .order_by(MovimentiModel.data_operazione)
        )
        return self.get_all(stmt, as_dataframe=True)

    def get_monthly_ext_to_conto(self) -> pd.DataFrame:
        """Get monthly aggregation of transactions from external accounts to conto."""
        return self.aggregate_by_date('month', MovimentiModel.importo,
                                      (MovimentiModel.is_entrata() & MovimentiModel.is_category(MovimentiCategory.Bonifici)) )

    def get_monthly_conto_to_ext(self) -> pd.DataFrame:
        """Get monthly aggregation of transactions from conto to external accounts."""
        return self.aggregate_by_date('month', MovimentiModel.importo,
                                      (MovimentiModel.is_uscita() & MovimentiModel.is_category(MovimentiCategory.Bonifici)) )

    def get_monthly_conto_to_portafoglio(self) -> pd.DataFrame:
        """Get monthly aggregation of entries and exits."""
        return self.aggregate_by_date('month', MovimentiModel.importo,
                                      (MovimentiModel.is_uscita() & MovimentiModel.is_category(MovimentiCategory.CompravenditaTitoli)))

    def get_monthly_portafoglio_to_conto(self) -> pd.DataFrame:
        """Get monthly aggregation of entries and exits."""
        return self.aggregate_by_date('month', MovimentiModel.importo,
                                      (MovimentiModel.is_entrata() & MovimentiModel.is_category(MovimentiCategory.CompravenditaTitoli)))


if __name__ == "__main__":
    movimenti_dao = Movimenti()
    # start_date = datetime(2025, 1, 1)
    # end_date = datetime(2025, 12, 31)
    # print(movimenti_dao.get_liquidita() )
    df = movimenti_dao.get_by_category(MovimentiCategory('Bonifici'))
    print(df)
