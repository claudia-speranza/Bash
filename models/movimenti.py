import pandas as pd

from models.basic import BasicTimedData


class Movimenti(BasicTimedData):
    """

    """
    @classmethod
    def adapt_excel(cls, records):
        records = records.fillna(0)
        records['Data'] = pd.to_datetime(records.Data, dayfirst=True)
        records['EntrateUscite'] = records.Entrate + records.Uscite
        records = records.sort_values('Data').reset_index(drop=True)
        return records

    @property
    def liquidita(self) -> float:
        return round(sum(self['EntrateUscite']), 2)

    def get_monthly_in_and_out(self):
        return self.monthly_aggregation({'Entrate': 'sum', 'Uscite': 'sum'})
