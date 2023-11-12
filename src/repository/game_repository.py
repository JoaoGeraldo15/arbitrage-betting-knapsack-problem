from typing import List, Dict, Any

from injectable import injectable
from sqlalchemy.orm import selectinload

from src.config.connection import DBConnection
from src.model.models import Game, Bookmaker, Market, Outcome


@injectable
class GameRepository:
    def find_all(self) -> List[Game]:
        with DBConnection() as db:
            return db.session.query(Game).join(Bookmaker).join(Market).join(Outcome)

    def find_paged(self, page_number=1, items_per_page=10) -> List[Game] and int:
        with DBConnection() as db:
            query = db.session.query(Game) \
                .options(selectinload(Game.bookmakers)
                         .selectinload(Bookmaker.markets)
                         .selectinload(Market.outcomes))
            restante = query.count() - (items_per_page * page_number)
            return query.offset((page_number - 1) * items_per_page).limit(items_per_page).all(), restante

    def save_all(self, events: List[Game]):
        with DBConnection() as db:
            db.session.add_all(events)
            db.session.commit()

    def find_all_by_id(self, ids: List[str]):
        with DBConnection() as db:
            return db.session.query(Game) \
                .options(
                selectinload(Game.bookmakers).selectinload(Bookmaker.markets).selectinload(Market.outcomes)).filter(
                Game.id.in_(ids)).all()

    def get_teams(self, ids: List[str]) -> dict:
        with DBConnection() as db:
            list_games = db.session.query(Game).filter(Game.id.in_(ids)).all()
            return { i.id : f'{i.home_team} x {i.away_team} [{i.sport_title}]' for i in list_games}
