from datetime import datetime

import numpy as np
import pandas as pd

from dataframes.basic import BasicTimedData


class Ordini(BasicTimedData):
    """
    Dataframe columns
    :param Data:
    :param DataValuta:
    :param Segno:
    :param SpeseTotali:
    :param EntrateUscite:
    """

    @classmethod
    def adapt_excel(cls, records):
        records = records.fillna(0)
        records['Data'] = pd.to_datetime(records.Operazione, dayfirst=True)
        del records['Operazione']
        records['DataValuta'] = pd.to_datetime(records.Valuta, dayfirst=True)
        del records['Valuta']
        records['Segno'] = np.where(records.Segno == 'A', 1, -1)
        records['SpeseTotali'] = (records.CommissioniFondiSw + records.CommissioniFondiBanca
                               + records.SpeseFondiSgr + records.CommissioniAmministrato)
        records['EntrateUscite'] = records.Controvalore * records.Segno + records.SpeseTotali
        records = records.sort_values('Data').reset_index(drop=True)
        return cls(records)

    @property
    def investimenti(self) -> float:
        return round(sum(self['EntrateUscite']), 2)

    def filter_by_isin(self, isin: str):
        return self.loc[self['Isin'] == isin]