from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, List, Any, Dict, Tuple

import pandas as pd
import psycopg2
from sqlalchemy import func, and_, asc, text
from sql.manager import DBInstance
from sql.models.basic import Base
from sql.utils import logger


class BasicDao(ABC):
    """A base class for handling data operations using SQLAlchemy."""
    db = DBInstance()

    def __init__(self, model_class: type):
        """
        Initialize with a database manager.

        Args:
            db_manager: A database manager instance
        """
        self.model_class = model_class
        self.table_name = model_class.__tablename__

    def insert_in_batch(self, data: List[Base]):
        """
            Process batch items individually when batch insert fails.
            Returns:
                Dict with individual processing results
            """
        results = {
            'success_count': 0,
            'failed_items': [],
            'errors': []
        }
        with self.db.session as session:
            for idx, item in enumerate(data):
                try:
                    session.add(item)
                    session.commit()
                    results['success_count'] += 1
                except Exception as item_error:
                    session.rollback()

                    results['errors'].append({
                        'index': idx,
                        'item': item,
                        'error': str(item_error)
                    })
                    if hasattr(item_error, 'orig') and isinstance(item_error.orig, psycopg2.errors.UniqueViolation):
                        logger.warn(f'Item {item} already exists, skipping.')
                    else:
                        logger.warn(f'Inserting item {item} raised exception {item_error}')

        return results

    def dataframe_to_sql(self, df: pd.DataFrame):
        """
        Convert a pandas DataFrame to a list of SQLAlchemy ORM instances.

        Args:
            df: The pandas DataFrame to convert

        Returns:
            List of ORM instances
        """
        records = []
        for _, row in df.iterrows():
            record_data = row.to_dict()
            record = self.model_class(**record_data)
            records.append(record)
        return records

    def insert_from_dataframe(self, df: pd.DataFrame) -> Tuple[bool, str]:
        try:
            processed = self.dataframe_to_sql(df)
            results = self.insert_in_batch(processed)
            if not results:
                msg = 'Something went wrong uploading file'
                return False, msg
            success_count, error_count = results['success_count'], len(results['errors'])
            msg = f'Successfully inserted {success_count} items into {self.table_name}. '
            if error_count:
                msg += f'Could not insert {error_count} items'
            return True, msg
        except Exception as e:
            msg = f'Something went wrong inserting dataframe in {self.table_name}: {e}'
            logger.warning(msg)
        return False,  msg


class BasicTimedDao(BasicDao, ABC):
    """A class for handling time-series data with filtering capabilities."""

    def get_in_timerange(self,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None) -> List[Any]:
        """
        Filter data between start_date and end_date.

        Args:
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering

        Returns:
            List: List of model instances between the specified dates

        Raises:
            ValueError: If start_date is after end_date
        """
        if start_date is not None and end_date is not None and start_date > end_date:
            raise ValueError("start_date cannot be after end_date")

        with self.db.session as session:
            query = session.query(self.model_class)

            if start_date is None:
                # Get the minimum date if start_date is not provided
                min_date_query = session.query(func.min(self.model_class.data_operazione)).scalar()
                start_date = min_date_query or datetime.min

            if end_date is None:
                end_date = datetime.now()

            # Apply date filter
            query = query.filter(
                and_(
                    self.model_class.data_operazione >= start_date,
                    self.model_class.data_operazione <= end_date
                )
            ).order_by(asc(self.model_class.data_operazione))

            return query.all()

    def aggregate_by_date_format(self,
                                date_format: str,
                                aggregations: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Aggregate data by a date format string.

        Args:
            date_format: PostgreSQL date format string (e.g., 'YYYY' for year)
            aggregations: Dictionary mapping column names to aggregate functions

        Returns:
            List[Dict]: Aggregated data
        """
        with self.db.get_session as session:
            # Prepare the SELECT part with date_trunc and aggregations
            select_clause = [text(f"to_char(data_operazione, '{date_format}') as period")]

            for column, agg_func in aggregations.items():
                select_clause.append(text(f"{agg_func}({column}) as {column}_{agg_func}"))

            # Create the query
            query = session.query(*select_clause).select_from(self.model_class)

            # Group by the date format
            query = query.group_by(text(f"to_char(data_operazione, '{date_format}')"))

            # Order by the period
            query = query.order_by(text("period"))

            # Execute and fetch results
            result = query.all()

            # Convert SQLAlchemy result to list of dictionaries
            return [dict(row._mapping) for row in result]

    def yearly_aggregation(self, aggregations: Dict[str, str]) -> List[Dict[str, Any]]:
        """Aggregate data by year."""
        return self.aggregate_by_date_format('YYYY', aggregations)

    def monthly_aggregation(self, aggregations: Dict[str, str]) -> List[Dict[str, Any]]:
        """Aggregate data by month and year."""
        return self.aggregate_by_date_format('YYYY-MM', aggregations)

    def daily_aggregation(self, aggregations: Dict[str, str]) -> List[Dict[str, Any]]:
        """Aggregate data by day, month and year."""
        return self.aggregate_by_date_format('YYYY-MM-DD', aggregations)
