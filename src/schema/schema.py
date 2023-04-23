from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel


class OutcomeBase(BaseModel):
    name: str
    price: float
    point: Optional[float]
    market_id: Optional[str]
    update_time: Optional[datetime]

    def __eq__(self, other):
        return self.name == other.name \
            and self.point == other.point \
            and self.price == other.price

    def __hash__(self):
        return hash((self.update_time.replace(tzinfo=datetime.timezone.utc), self.name, self.point, self.price))

    class Config:
        orm_mode = True


class MarketBase(BaseModel):
    key: str
    last_update: datetime
    outcomes: List[OutcomeBase]
    bookmaker_id: Optional[str]

    def __eq__(self, other):
        return self.key == other.key \
        and self.last_update == other.last_update \
        and self.outcomes == other.outcomes

    def __hash__(self):
        return hash((self.key, self.last_update, self.outcomes))

    class Config:
        orm_mode = True


class BookmakerBase(BaseModel):
    key: str
    title: str
    last_update: Optional[datetime]
    markets: List[MarketBase]
    game_id: Optional[str]

    def __eq__(self, other):
        return self.key == other.key \
        and self.last_update == other.last_update \
        and self.markets == other.markets

    def __hash__(self):
        return hash((self.key, self.last_update, self.markets))

    class Config:
        orm_mode = True


class GameBase(BaseModel):
    id: str
    sport_key: str
    sport_title: str
    commence_time: datetime
    home_team: str
    away_team: str
    bookmakers: List[BookmakerBase]

    def __eq__(self, other):
        return self.sport_key == other.sport_key \
        and self.commence_time == other.commence_time \
        and self.home_team == other.home_team \
        and self.away_team == other.away_team \
        and self.bookmakers == other.bookmakers

    def __hash__(self):
        return hash((self.sport_key, self.commence_time, self.home_team, self.away_team, self.bookmakers))

    class Config:
        orm_mode = True


class EventBase(BaseModel):
    id: Optional[int]
    sport_key: str
    sport_title: str
    commence_time: datetime
    home_team: str
    away_team: str
    home_score: Optional[int]
    away_score: Optional[int]
    covered: bool
    event_id: int
    roundInfo: int

    class Config:
        orm_mode = True
