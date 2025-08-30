import logging
from datetime import datetime
from typing import List, Optional

import pandas as pd

from db.daos.basic import BasicTimedDao
from db.models.ordini import OrdiniModel
from db.utils import clean_numeric_value, ensure_datetime, logger


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

    def insert_from_dataframe(self, df: pd.DataFrame) -> Optional[dict]:
        """
           Process and clean the DataFrame data for database insertion.

           Args:
               df: Raw DataFrame from CSV

           Returns:
               List of dictionaries ready for database insertion
           """
        try:
            processed_data = []

            for index, row in df.iterrows():
                # Skip rows with missing essential data
                try:
                    data_operazione = ensure_datetime(row['Operazione'])
                    data_valuta = ensure_datetime(row['Data valuta'])
                except Exception as e:
                    logger.warn('Error parsing dates in Movimenti, skipping row')
                    continue
                isin = row.get('Isin', None)
                descrizione = row.get('Descrizione', '')
                segno = row.get('Segno', 0)
                segno = 1 if segno == 'A' else (-1 if segno == 'V' else 0)
                quantita = clean_numeric_value(row.get('Quantita', 0))
                divisa = row.get('Divisa', 'EUR')
                cambio = clean_numeric_value(row.get('Cambio', 0))
                prezzo = clean_numeric_value(row.get('Prezzo', 0))
                controvalore = clean_numeric_value(row.get('Controvalore', 0))
                commissioni_fondi_sw = clean_numeric_value(row.get('Commissioni Fondi Sw/Ingr/Uscita', 0))
                commissioni_fondi_banca = clean_numeric_value(row.get('Commissioni Fondi Banca Corrispondente', 0))
                spese_fondi_sgr = clean_numeric_value(row.get('Spese Fondi Sgr', 0))
                commissioni_amministrato = clean_numeric_value(row.get('Commissioni amministrato', 0))

                # Prepare record
                record = OrdiniModel(
                    data_operazione=data_operazione,
                    data_valuta = data_valuta,
                    isin = isin,
                    descrizione = descrizione,
                    segno = segno,
                    quantita = quantita,
                    divisa = divisa,
                    cambio = cambio,
                    prezzo = prezzo,
                    controvalore =controvalore,
                    commissioni_fondi_sw = commissioni_fondi_sw,
                    commissioni_fondi_banca = commissioni_fondi_banca,
                    spese_fondi_sgr = spese_fondi_sgr,
                    commissioni_amministrato=commissioni_amministrato
                )
                processed_data.append(record)

            results = self.insert_in_batch(processed_data)
            return results
        except Exception as e:
            logging.warning(f'Something went wrong inserting dataframe in Ordini: {e}')
        return None