import logging
import os

from sqlalchemy import URL, create_engine
from sqlalchemy.orm import sessionmaker, Session

from sql.models.basic import Base


class DBInstance:
    """A singleton class to manage database connections and session creation."""

    _instance = None
    _initialized = False

    def __new__(cls):
        """Create a new instance or return the existing one."""
        if cls._instance is None:
            cls._instance = super(DBInstance, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the database manager (only once).
        """
        if self._initialized:
            return

        url_object = URL.create(
            "postgresql",
            username=os.getenv('POSTGRES_USER', ''),
            password=os.getenv('POSTGRES_PASSWORD', ''),
            host='localhost',
            port=os.getenv('POSTGRES_PORT', 5432),
            database=os.getenv('POSTGRES_DB'),
        )
        self.engine = create_engine(url_object)
        self.SessionMaker = sessionmaker(bind=self.engine)
        self.create_all_tables()
        # Mark as initialized to prevent re-initialization
        DBInstance._initialized = True

    def create_all_tables(self):
        """Create all tables defined in the models."""
        logging.info('Adding missing tables to database')
        Base.metadata.create_all(self.engine)

    @property
    def session(self) -> Session:
        """Get a new database session."""
        return self.SessionMaker()

    @classmethod
    def get_instance(cls):
        """Get the singleton instance (alternative access method)."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance