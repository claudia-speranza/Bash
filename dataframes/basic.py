from datetime import datetime
from typing import Optional

import pandas as pd


class BasicData(pd.DataFrame):
    """A base class for handling data operations, inheriting from pandas DataFrame."""

    @classmethod
    def from_excel(cls, file_path: str) -> 'BasicData':
        """
        Create a BasicData instance from an Excel file.

        Args:
            file_path (str): Path to the Excel file

        Returns:
            BasicData: New instance with data from Excel file

        Raises:
            FileNotFoundError: If the Excel file doesn't exist
            ValueError: If the Excel file is empty or corrupted
        """
        try:
            df = pd.read_excel(file_path)
            if df.empty:
                raise ValueError("Excel file is empty")
            return cls.adapt_excel(df)
        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file not found at path: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")

    @property
    def _constructor(self):
        return type(self)

    @classmethod
    def adapt_excel(cls, records):
        return cls(records)



class BasicTimedData(BasicData):
    """A class for handling time-series data with filtering capabilities."""

    def filtered(self,
                 start_date: Optional[datetime] = None,
                 end_date: Optional[datetime] = None) -> 'BasicTimedData':
        """
        Filter data between start_date and end_date.

        Args:
            start_date (datetime, optional): Start date for filtering. Defaults to earliest date.
            end_date (datetime, optional): End date for filtering. Defaults to current date.

        Returns:
            BasicTimedData: Filtered data between the specified dates

        Raises:
            ValueError: If start_date is after end_date
        """
        if start_date is None:
            start_date = self['Data'].min()
        if end_date is None:
            end_date = datetime.now()

        if start_date > end_date:
            raise ValueError("start_date cannot be after end_date")

        mask = (self['Data'] >= start_date) & (self['Data'] <= end_date)
        # Convert the filtered DataFrame back to BasicTimedData
        return type(self)(self.loc[mask])

    def aggregate_by_strftime(self, strftime: str, aggregation: dict) -> pd.DataFrame:
        monthly_data = self.groupby(self.Data.dt.strftime(strftime)).agg(aggregation).reset_index()
        return monthly_data

    def yearly_aggregation(self, aggregation: dict):
        return self.aggregate_by_strftime('%Y', aggregation)

    def monthly_aggregation(self, aggregation: dict):
        return self.aggregate_by_strftime('%Y-%m', aggregation)

    def daily_aggregation(self, aggregation: dict):
        return  self.aggregate_by_strftime('%Y-%m-%d', aggregation)



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