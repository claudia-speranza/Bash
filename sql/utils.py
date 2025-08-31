import logging
from datetime import datetime
from typing import Optional, Any
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clean_numeric_value(value) -> float:
    """
    Clean and convert numeric values to float.
    Handles empty strings, NaN values, and comma decimal separators.

    Args:
        value: Raw numeric value from CSV

    Returns:
        Float value or 0.0 if conversion fails
    """
    if pd.isna(value) or value == '' or value is None:
        return 0.0

    try:
        # Handle string values with comma as decimal separator
        if isinstance(value, str):
            # Remove any whitespace and replace comma with dot
            clean_value = value.strip().replace(',', '.')
            # Handle negative values with minus sign
            if clean_value.startswith('-'):
                return -float(clean_value[1:])
            return float(clean_value)

        return float(value)
    except (ValueError, TypeError):
        logger.warning(f"Could not convert to float: {value}")
        return 0.0


def ensure_datetime(date_var: Any, date_format: str = '%d/%m/%Y') -> datetime:
    """
    Convert a date variable to datetime if it's not already a pandas Timestamp or datetime.

    Args:
        date_var: The date variable to check and potentially convert
        date_format: Format string for parsing string dates (default: '%d/%m/%Y')

    Returns:
        datetime: A datetime object

    Raises:
        ValueError: If the date cannot be parsed with the given format
        TypeError: If the input type is not supported
    """

    # Check if it's already a pandas Timestamp
    if isinstance(date_var, pd.Timestamp):
        return date_var.to_pydatetime()

    # Check if it's already a datetime
    if isinstance(date_var, datetime):
        return date_var

    # Check if it's a string and try to parse it
    if isinstance(date_var, str):
        try:
            return datetime.strptime(date_var, date_format)
        except ValueError as e:
            raise ValueError(f"Cannot parse date '{date_var}' with format '{date_format}': {e}")

    # Check if it's a date object (without time)
    if hasattr(date_var, 'year') and hasattr(date_var, 'month') and hasattr(date_var, 'day'):
        try:
            return datetime.combine(date_var, datetime.min.time())
        except Exception as e:
            raise TypeError(f"Cannot convert date object to datetime: {e}")

    # Check if it's NaT (Not a Time) or NaN
    if pd.isna(date_var):
        raise ValueError("Cannot convert NaT/NaN to datetime")

    # Try to convert using pandas (handles various formats)
    try:
        return pd.to_datetime(date_var, format=date_format).to_pydatetime()
    except Exception as e:
        raise TypeError(f"Unsupported date type '{type(date_var)}' for value '{date_var}': {e}")


def read_excel_file(file_path: str, **kwargs) -> pd.DataFrame:
    try:
        df = pd.read_csv(file_path, encoding='utf-8', **kwargs)
    except Exception as e:
        try:
            df = pd.read_excel(file_path, engine='openpyxl', **kwargs)
        except Exception as e:
            # Try with xlrd engine for older Excel files
            try:
                df = pd.read_excel(file_path, engine='xlrd', **kwargs)
            except Exception as e2:
                logging.error(
                    f"Could not read Excel file with any engine. Original errors: openpyxl: {e}, xlrd: {e2}")
                return None
    return df


def convert_file_to_table(file_path) -> Optional[pd.DataFrame]:
    df = read_excel_file(file_path, header=None)
    if df is not None:
        num_cols = len(df.columns)
        idx = 0
        # Analyze each row
        for idx, row in df.iterrows():
            non_null = row.notna().sum()
            if non_null == num_cols:
                break
        df = read_excel_file(file_path, skiprows=idx, parse_dates=True, date_format='%d/%m/%Y')
        if df is not None:
            # Remove any completely empty rows
            df = df.dropna(how='all')

            # Clean column names (remove any extra whitespace)
            df.columns = df.columns.str.strip()
            return df
    return None

