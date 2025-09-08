from datetime import datetime
from typing import List, Optional, Dict

import numpy as np
import pandas as pd
from sqlalchemy import select, func, and_, asc, text

from sql.daos.basic import BasicTimedDao
from sql.models.ordini import OrdiniModel


class Ordini(BasicTimedDao):
    """Class for handling orders data."""

    def __init__(self):
        super().__init__(OrdiniModel)

    def get_by_isin(self, isin: str) -> pd.DataFrame:
        """Filter orders by ISIN."""
        stmt = (
            select(OrdiniModel)
            .where(OrdiniModel.isin == isin)
            .order_by(asc(OrdiniModel.data_operazione))
        )
        return self.get_all(stmt, True)

def analyze_orders(ordini: List[OrdiniModel]) -> Dict:
    ordini_acquisto = [ordine for ordine in ordini if ordine.prezzo != 0 and ordine.importo < 0]
    ordini_vendita = [ordine for ordine in ordini if ordine.prezzo != 0 and ordine.importo > 0]
    quantita_comprata = sum([ordine.quantita for ordine in ordini_acquisto])
    prezzo_medio = (sum([ordine.prezzo * ordine.quantita for ordine in ordini_acquisto]) /
                    quantita_comprata) if quantita_comprata != 0 else 0
    quantita_venduta = sum([ordine.quantita for ordine in ordini_vendita])
    incassi_netti = (sum([ordine.importo for ordine in ordini if ordine.prezzo == 0])  # incassi da dividendi
               + sum([ordine.importo for ordine in ordini_vendita])                    # incassi da vendite
               - quantita_venduta*prezzo_medio)                                        # costi di acquisto delle vendite
    commissioni = sum([ordine.commissione for ordine in ordini])
    return dict(
        prezzo_medio=round(prezzo_medio, 2),
        quantita=round(quantita_comprata - quantita_venduta, 2),
        quantita_comprata=round(quantita_comprata, 2),
        quantita_venduta=round(quantita_venduta, 2),
        incassi_netti=round(incassi_netti, 2),
        commissioni=round(commissioni, 2)
    )

def analyze_orders_df(ordini_df: pd.DataFrame) -> Dict:
    ordini_acquisto = ordini_df[(ordini_df['prezzo'] != 0) & (ordini_df['importo'] < 0)]
    ordini_vendita = ordini_df[(ordini_df['prezzo'] != 0) & (ordini_df['importo'] > 0)]
    quantita_comprata = ordini_acquisto['quantita'].sum()
    prezzo_medio = (np.average(ordini_acquisto['prezzo'], weights=ordini_acquisto['quantita'])
                    if quantita_comprata != 0 else 0)
    quantita_venduta = ordini_vendita['quantita'].sum()
    incassi_netti = (ordini_df[ordini_df['prezzo'] == 0]['importo'].sum()  # incassi da dividendi
               + ordini_vendita['importo'].sum()                           # incassi da vendite
               - quantita_venduta*prezzo_medio)                            # costi di acquisto delle vendite
    commissioni = ordini_df['commissione'].sum()
    return dict(
        prezzo_medio=round(prezzo_medio, 2),
        quantita=round(quantita_comprata-quantita_venduta, 2),
        quantita_comprata=round(quantita_comprata, 2),
        quantita_venduta=round(quantita_venduta, 2),
        incassi_netti=round(incassi_netti, 2),
        commissioni=round(commissioni, 2)
    )

if __name__ == "__main__":
    Ordini()