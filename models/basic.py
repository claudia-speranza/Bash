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
            return cls.from_records(cls.adapt_excel(df))
        except FileNotFoundError:
            raise FileNotFoundError(f"Excel file not found at path: {file_path}")
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")

    @classmethod
    def adapt_excel(cls, records):
        return records



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