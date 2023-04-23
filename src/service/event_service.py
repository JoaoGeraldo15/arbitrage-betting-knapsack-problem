import datetime
import json
from typing import List

from injectable import autowired, Autowired, injectable

from src.config.connection import DBConnection
from src.model.models import Event
from src.repository.event_repository import EventRepository
from src.schema import EventBase


@injectable
class EventService:
    @autowired
    def __init__(self, repository: Autowired(EventRepository)):
        self.repository = repository

    @classmethod
    def save_events(cls):
        with open("events/events_UTC.json", "r") as file:
            data = json.load(file)
        events_base = [EventBase(**event) for event in data]

        events = [Event.from_schema(event) for event in events_base]
        with DBConnection() as db:
            db.session.add_all(events)
            db.session.commit()

    def get_events_utc_date(self) -> List[Event]:
        horario = datetime.datetime.now(datetime.timezone.utc)
        return self.repository.find_all_by_date(horario.date())


def te():
    event_service = EventService()
    events = event_service.get_events_utc_date()

    for i in events:
        print(i)

if __name__ == '__main__':
    EventService.save_events()


