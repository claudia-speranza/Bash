import re

import pandas as pd

from dataframes.basic import BasicTimedData


class Movimenti(BasicTimedData):
    """

    """
    @classmethod
    def adapt_excel(cls, records):
        records = records.fillna(0)
        records['Data'] = pd.to_datetime(records.Data, dayfirst=True)
        records['EntrateUscite'] = records.Entrate + records.Uscite
        records = records.sort_values('Data').reset_index(drop=True)
        return cls(records)

    @property
    def liquidita(self) -> float:
        return round(sum(self['EntrateUscite']), 2)

    def get_imposte_di_bollo(self):
        def extract_date(description):
            # Find the date in the format dd.mm.yyyy
            match = re.search(r'(\d{2}\.\d{2}\.\d{4})', description)
            if match:
                return pd.to_datetime(match.group(1), format='%d.%m.%Y')
            return None  # If no date is found, return None

        filtered_db = self.loc[self['Descrizione'] == 'Imposta bollo conto corrente']
        filtered_db['DataRef'] = filtered_db['DescrizioneCompleta'].apply(extract_date)
        filtered_db['Importo'] = filtered_db['EntrateUscite']
        return filtered_db.filter(items=['Data', 'Importo', 'DataRef'])

    def get_imposte_dossier(self):
        def extract_dossier(description):
            return description.split(' ')[-1]
        filtered_db = self.loc[self['Descrizione'] == 'Imposta bollo dossier titoli']
        filtered_db['Dossier'] = filtered_db['DescrizioneCompleta'].apply(extract_dossier)
        filtered_db['Importo'] = filtered_db['EntrateUscite']
        return filtered_db.filter(items=['Data', 'Importo', 'Dossier'])

    def get_monthly_in_and_out(self):
        return self.monthly_aggregation({'Entrate': 'sum', 'Uscite': 'sum'})
