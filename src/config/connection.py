from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.config.config import DATABASE_URL
from src.model.models import *


class DBConnection:
    def __init__(self):
        self.__connection_string = DATABASE_URL
        self.__engine = self.__create_database_engine()
        self.session: Session()
        self.__create_db_if_not_exists()

    def __create_database_engine(self):
        engine = create_engine(self.__connection_string, echo=False)
        return engine

    def get_engine(self):
        return self.__engine

    def __enter__(self):
        session_make = sessionmaker(bind=self.__engine)
        self.session = session_make()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def __create_db_if_not_exists(self):
        Base.metadata.create_all(bind=self.__engine, checkfirst=True)