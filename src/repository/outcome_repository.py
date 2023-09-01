from typing import List
from injectable import injectable

from src.config.connection import DBConnection
from src.model.models import Outcome


@injectable
class OutcomeRepository:

    def find_all_points(self) -> List[float]:
        with DBConnection() as db:
            return db.session.query(Outcome.point).filter(
                Outcome.point != None).group_by(Outcome.point).order_by(Outcome.point)

    def find_all(self, point=1.0) -> List[Outcome]:
        with DBConnection() as db:
            return db.session.query(Outcome).filter(
                Outcome.point == point).all()

    def find_all_by_ids(self, ids: List[int]) -> List[Outcome]:
        with DBConnection() as db:
            return db.session.query(Outcome).filter(Outcome.id.in_(ids)).all()
