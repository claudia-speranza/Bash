from abc import ABC
from datetime import datetime
from typing import Optional, List, Any, Dict, Tuple, Union

import pandas as pd
import psycopg2
from sqlalchemy import select, func, and_, asc, text
from sql.manager import DBInstance
from sql.models.basic import Base, OperationBase
from sql.utils import logger


class BasicDao(ABC):
    """A base class for handling data operations using SQLAlchemy."""
    db = DBInstance()
    model_class: type(Base)

    def __init__(self, model_class: type(Base)):
        """
        Initialize with a database manager.

        Args:
            db_manager: A database manager instance
        """
        self.model_class = model_class
        self.table_name = model_class.__tablename__
        self.create_table()

    def create_table(self):
        """Create all tables defined in the models."""
        Base.metadata.create_all(self.db.engine, tables=[self.model_class.__table__])
        logger.info(f'Table {self.table_name} ready in database')

    def insert(self, data: List[Base]):
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
            results = self.insert(processed)
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

    def get_all(self, stmt = None, as_dataframe: bool = False) -> Union[List[Base], pd.DataFrame]:
        """
        Retrieve all records from the table.

        Returns:
            List of all model instances
        """
        stmt = select(self.model_class) if stmt is None else stmt
        with self.db.session as session:
            if as_dataframe:
                df = pd.read_sql(stmt, session.bind)
                return df
            return session.execute(stmt).scalars().all()

    def get_one(self, stmt):
        with self.db.session as session:
            return session.execute(stmt).scalar_one_or_none()


class BasicTimedDao(BasicDao, ABC):
    """A class for handling time-series data with filtering capabilities."""
    model_class: type(OperationBase)

    def get_in_timerange(self,
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         as_dataframe: bool = False) -> Union[List[Base], pd.DataFrame]:
        """
        Filter data between start_date and end_date.
        """
        stmt = (
            select(self.model_class)
            .where(self.model_class.in_timerange(start_date, end_date))
            .order_by(asc(self.model_class.data_operazione))
        )
        return self.get_all(stmt, as_dataframe=as_dataframe)

    def aggregate_by_date(self, interval: str, column, where = None) -> pd.DataFrame:
        stmt = (select(
            func.date_trunc(interval, self.model_class.data_operazione).label(interval),
            func.sum(column).label('total')
        ))
        if where is not None:
            stmt = stmt.where(where)
        stmt = (stmt.group_by(
            func.date_trunc(interval, self.model_class.data_operazione)
        ).order_by(
            func.date_trunc(interval, self.model_class.data_operazione)
        ))
        return self.get_all(stmt, as_dataframe=True)