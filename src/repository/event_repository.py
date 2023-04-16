import datetime
from typing import List

from injectable import injectable
from sqlalchemy import func

from src.config.connection import DBConnection
from src.model.models import Event


@injectable
class EventRepository:
    def __init__(self):
        pass

    def find_all(self):
        with DBConnection() as db:
            return db.session.query(Event).all()

    def find_all_by_date(self, date: datetime.date):
        with DBConnection() as db:
            events: List[Event] = db.session.query(Event).filter(
                func.date(Event.commence_time) == date).all()
        return events

    def save_all(self, event: List[Event]):
        pass
