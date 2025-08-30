import logging
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import pandas as pd

from sql.daos.basic import BasicTimedDao
from sql.models.movimenti import MovimentiModel
from sql.utils import clean_numeric_value, ensure_datetime, logger, dataframe_to_sql


class Movimenti(BasicTimedDao):
    """Class for handling banking movements data."""

    def __init__(self):
        super().__init__(MovimentiModel)

    def get_liquidita(self, start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> float:
        """Calculate total liquidity (sum of entrate_uscite)."""
        filtered = self.get_in_timerange(start_date, end_date)
        # Calculate total from the filtered results
        total = sum(order.importo for order in filtered)
        return total

    def get_imposte_di_bollo(self) -> List[Dict[str, Any]]:
        """Get account stamp duty taxes."""
        with self.db.get_session() as session:
            query = session.query(
                MovimentiModel.data_operazione,
                MovimentiModel.totale.label('importo'),
                MovimentiModel.descrizione_completa
            ).filter(MovimentiModel.descrizione == 'Imposta bollo conto corrente')

            results = []
            for row in query.all():
                # Extract the reference date
                data_ref = None
                if row.descrizione_completa:
                    match = re.search(r'(\d{2}\.\d{2}\.\d{4})', row.descrizione_completa)
                    if match:
                        try:
                            data_ref = datetime.strptime(match.group(1), '%d.%m.%Y')
                        except ValueError:
                            pass

                results.append({
                    'data': row.data_operazione,
                    'importo': row.importo,
                    'data_ref': data_ref
                })

            return results

    def get_imposte_dossier(self) -> List[Dict[str, Any]]:
        """Get dossier stamp duty taxes."""
        with self.db.get_session() as session:
            query = session.query(
                MovimentiModel.data_operazione,
                MovimentiModel.totale.label('importo'),
                MovimentiModel.descrizione_completa
            ).filter(MovimentiModel.descrizione == 'Imposta bollo dossier titoli')

            results = []
            for row in query.all():
                # Extract the dossier number
                dossier = None
                if row.descrizione_completa:
                    parts = row.descrizione_completa.split(' ')
                    if parts:
                        dossier = parts[-1]

                results.append({
                    'data': row.data_operazione,
                    'importo': row.importo,
                    'dossier': dossier
                })

            return results

    def get_monthly_in_and_out(self) -> List[Dict[str, Any]]:
        """Get monthly aggregation of entries and exits."""
        return self.monthly_aggregation({'entrate': 'sum', 'uscite': 'sum'})

