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
