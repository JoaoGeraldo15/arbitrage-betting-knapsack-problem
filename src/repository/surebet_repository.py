from typing import List

from injectable import injectable

from src.config.connection import DBConnection
from src.model.models import Surebet


@injectable
class SurebetRepository:

    def save_all(self, surebets: List[Surebet]):
        with DBConnection() as db:
            db.session.add_all(surebets)
            db.session.commit()


    def find_all(self) -> List[Surebet]:
        with (DBConnection() as db):
            return db.session.query(Surebet).all()

    def find_all_between(self, start_date='2023-09-02 00:00:00', end_date='2023-09-02 23:59:59') -> List[Surebet]:
        with (DBConnection() as db):
            return db.session.query(Surebet).filter(
                Surebet.last_update_UNDER.between(start_date, end_date)).all()
