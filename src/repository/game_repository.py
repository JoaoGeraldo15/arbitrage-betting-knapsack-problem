from typing import List

from injectable import injectable
from sqlalchemy.orm import selectinload

from src.config.connection import DBConnection
from src.model.models import Game, Bookmaker, Market, Outcome

@injectable
class GameRepository:
    def find_all(self) -> List[Game]:
        with DBConnection() as db:
            return db.session.query(Game).join(Bookmaker).join(Market).join(Outcome)

    def save_all(self, events: List[Game]):
        with DBConnection() as db:
            db.session.add_all(events)
            db.session.commit()


    def find_all_by_id(self, ids: List[str]):
        with DBConnection() as db:
            return db.session.query(Game)\
                .options(selectinload(Game.bookmakers).selectinload(Bookmaker.markets).selectinload(Market.outcomes)).filter(Game.id.in_(ids)).all()