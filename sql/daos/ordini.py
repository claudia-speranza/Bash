from typing import List, Dict

import pandas as pd
from sqlalchemy import select, asc

from sql.daos.basic import BasicTimedDao
from sql.models.ordini import OrdiniModel


class Ordini(BasicTimedDao):
    """Class for handling orders data."""

    def __init__(self):
        super().__init__(OrdiniModel)

    def get_by_isin(self, isin: str, as_dataframe: bool = True) -> pd.DataFrame:
        """Filter orders by ISIN."""
        stmt = (
            select(OrdiniModel)
            .where(OrdiniModel.isin == isin)
            .order_by(asc(OrdiniModel.data_operazione))
        )
        return self.get_all(stmt, as_dataframe)

def analyze_orders(ordini: List[OrdiniModel], strumento: str) -> Dict:
    # acquisto
    ordini_acquisto = [ordine for ordine in ordini if ordine.prezzo != 0 and ordine.importo < 0]
    quantita_comprata = sum([ordine.quantita for ordine in ordini_acquisto])
    prezzo_medio_acquisto = (sum([ordine.prezzo * ordine.quantita for ordine in ordini_acquisto]) /
                    quantita_comprata) if quantita_comprata != 0 else 0
    if strumento == 'Obbligazione':  # per le obbligazioni consideriamo il prezzo di carico come 100
        prezzo_medio_acquisto /= 100
    # vendita
    ordini_vendita = [ordine for ordine in ordini if ordine.prezzo != 0 and ordine.importo > 0]
    quantita_venduta = sum([ordine.quantita for ordine in ordini_vendita])
    prezzo_medio_vendita = (sum([ordine.prezzo * ordine.quantita for ordine in ordini_vendita]) /
                             quantita_venduta) if quantita_venduta != 0 else 0
    if strumento == 'Obbligazione':  # per le obbligazioni consideriamo il prezzo di carico come 100
        prezzo_medio_vendita /= 100

    commissioni = sum([ordine.commissione for ordine in ordini])
    incassi_netti = (sum([ordine.importo for ordine in ordini if ordine.prezzo == 0])  # incassi da dividendi
               + sum([ordine.importo for ordine in ordini_vendita])                    # incassi da vendite
               - quantita_venduta*prezzo_medio_acquisto
                     - commissioni)                                        # costi di acquisto delle vendite
    rendimento = incassi_netti / (quantita_venduta * prezzo_medio_acquisto) if (quantita_venduta > 0 and prezzo_medio_acquisto > 0) else 0 # income / partimonio investito
    return dict(
        prezzo_medio_acquisto=round(prezzo_medio_acquisto, 2),
        prezzo_medio_vendita=round(prezzo_medio_vendita, 2),
        quantita=round(quantita_comprata - quantita_venduta, 2),
        valore_di_carico=round(quantita_comprata * prezzo_medio_acquisto, 2),
        quantita_comprata=round(quantita_comprata, 2),
        quantita_venduta=round(quantita_venduta, 2),
        incassi_netti=round(incassi_netti, 2),
        commissioni=round(commissioni, 2),
        rendimento=round(rendimento, 2)
    )

if __name__ == "__main__":
    Ordini()