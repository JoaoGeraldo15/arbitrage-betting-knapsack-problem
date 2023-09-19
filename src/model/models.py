import datetime
from dataclasses import dataclass

from sqlalchemy import Column, String, ForeignKey, Integer, Float, DateTime, Boolean
from sqlalchemy.orm import relationship

from src.config.config import Base
from src.schema.schema import GameBase, BookmakerBase, MarketBase, OutcomeBase, EventBase


@dataclass
class Outcome(Base):
    __tablename__ = "OUTCOME"
    id = Column(Integer, primary_key=True)
    name = Column("name", String)
    price = Column("price", Float)
    point = Column("point", Float)
    update_time = Column("last_update", DateTime(timezone=False))
    market_id = Column(Integer, ForeignKey("MARKET.id"))
    market = relationship('Market', back_populates='outcomes')

    @classmethod
    def from_schema(cls, outcome_schema: OutcomeBase, update_time) -> "Outcome":
        outcome_schema['update_time'] = update_time
        return cls(**outcome_schema)

    def __eq__(self, other):
        return self.update_time.replace(tzinfo=datetime.timezone.utc) == other.update_time \
            and self.name == other.name \
            and self.point == other.point \
            and self.price == other.price

    def __hash__(self):
        return hash((self.update_time.replace(tzinfo=datetime.timezone.utc), self.name, self.point, self.price))

    def __repr__(self):
        return f"name={self.name}, price={self.price}, point={self.point}, update_time={self.update_time}"


@dataclass
class Market(Base):
    __tablename__ = "MARKET"
    id = Column("id", Integer, primary_key=True)
    key = Column("key", String)
    last_update = Column("last_update", DateTime(timezone=False))
    outcomes = relationship('Outcome', back_populates='market', cascade="all, delete, delete-orphan")
    bookmaker_id = Column(Integer, ForeignKey("BOOKMAKER.id"))
    bookmaker = relationship('Bookmaker', back_populates='markets')

    @classmethod
    def from_schema(cls, market_schema: MarketBase) -> "Market":
        outcomes = [Outcome.from_schema(o, update_time=market_schema['last_update']) for o in market_schema['outcomes']]
        market_schema['last_update'] = market_schema['last_update']
        del market_schema['outcomes']
        return cls(**market_schema, outcomes=outcomes)

    def __eq__(self, other):
        return self.key == other.key \
            and self.last_update == other.last_update \
            and self.outcomes == other.outcomes

    def __hash__(self):
        return hash((self.key, self.last_update, self.outcomes))

    def __repr__(self):
        return f"key={self.key}, last_update={self.last_update}, outcomes={self.outcomes}"



@dataclass
class Bookmaker(Base):
    __tablename__ = "BOOKMAKER"
    id = Column("id", Integer, primary_key=True)
    key = Column("key", String)
    title = Column("title", String)
    last_update = Column("last_update", DateTime(timezone=False))
    markets = relationship('Market', back_populates='bookmaker', cascade="all, delete, delete-orphan")
    game_id = Column(String, ForeignKey("GAME.id"))
    game = relationship("Game", back_populates="bookmakers")

    @classmethod
    def from_schema(cls, bookmaker_schema: BookmakerBase) -> "Bookmaker":
        markets = [Market.from_schema(m) for m in bookmaker_schema['markets']]
        bookmaker_schema['last_update'] = bookmaker_schema['last_update']
        del bookmaker_schema['markets']
        return cls(**bookmaker_schema, markets=markets)

    def __eq__(self, other):
        return self.key == other.key \
            and self.last_update == other.last_update \
            and self.markets == other.markets

    def __hash__(self):
        return hash((self.key, self.last_update, self.markets))

    def __repr__(self):
        return f"key={self.key}, title={self.title}, last_update={self.last_update}, markets={self.markets}"


@dataclass
class Game(Base):
    __tablename__ = "GAME"
    id = Column("id", String, primary_key=True)
    sport_key = Column("sport_key", String)
    sport_title = Column("sport_title", String)
    commence_time = Column("commence_time", DateTime(timezone=False))
    home_team = Column("home_team", String)
    away_team = Column("away_team", String)
    event_id = Column(Integer, ForeignKey('EVENT.id'))
    event = relationship("Event", uselist=False)
    bookmakers = relationship("Bookmaker", back_populates="game", cascade="all, delete, delete-orphan")

    @classmethod
    def from_schema(cls, game_schema: GameBase) -> "Game":
        game_dict = game_schema.dict()
        bookmakers = [Bookmaker.from_schema(b) for b in game_dict['bookmakers']]
        game_dict['commence_time'] = game_dict['commence_time']
        del game_dict['bookmakers']
        return cls(**game_dict, bookmakers=bookmakers)

    def __repr__(self):
        return f"id={self.id}, commence_time={self.commence_time}, bookmakers={self.bookmakers}"

    def __eq__(self, other):
        return self.sport_key == other.sport_key \
            and self.commence_time == other.commence_time \
            and self.home_team == other.home_team \
            and self.away_team == other.away_team \
            and self.bookmakers == other.bookmakers

    def __hash__(self):
        return hash((self.sport_key, self.commence_time, self.home_team, self.away_team, self.bookmakers))


@dataclass
class Event(Base):
    __tablename__ = "EVENT"
    id = Column("id", Integer, primary_key=True)
    sport_key = Column("sport_key", String)
    sport_title = Column("sport_title", String)
    commence_time = Column("commence_time", DateTime(timezone=False))
    home_team = Column("home_team", String)
    away_team = Column("away_team", String)
    home_score = Column("home_score", Integer)
    away_score = Column("away_score", Integer)
    covered = Column("covered", Boolean)
    event_id = Column('event_id', Integer)
    roundInfo = Column("roundInfo", Integer)

    @classmethod
    def from_schema(cls, event_schema: EventBase) -> "Event":
        event_dict = event_schema.dict()
        event_dict['commence_time'] = event_schema.commence_time.replace(tzinfo=datetime.timezone.utc)
        return cls(**event_dict)

    def __repr__(self):
        return f"event_id={self.event_id}, sport_key={self.sport_key}, commence_time={self.commence_time}, home_team={self.home_team}, away_team={self.away_team}"


@dataclass
class Surebet(Base):
    __tablename__ = "SUREBET"
    game_id = Column("game_id", String, ForeignKey('GAME.id'), primary_key=True)
    outcome_id_OVER = Column("outcome_id_OVER", Integer, ForeignKey('OUTCOME.id'), primary_key=True)
    outcome_id_UNDER = Column("outcome_id_UNDER", Integer, ForeignKey('OUTCOME.id'), primary_key=True)
    bookmaker_key_OVER = Column("bookmaker_key_OVER", String)
    bookmaker_key_UNDER = Column("bookmaker_key_UNDER", String)
    odd_OVER = Column("odd_OVER", Float)
    odd_UNDER = Column("odd_UNDER", Float)
    last_update_OVER = Column("last_update_OVER", DateTime(timezone=False))
    last_update_UNDER = Column("last_update_UNDER", DateTime(timezone=False))
    profit = Column("profit", Float)

    def __init__(self, game_id, outcome_id_OVER, outcome_id_UNDER, bookmaker_key_OVER,
                 bookmaker_key_UNDER, odd_OVER, odd_UNDER, profit):
        self.game_id = game_id
        self.outcome_id_OVER = outcome_id_OVER
        self.outcome_id_UNDER = outcome_id_UNDER
        self.bookmaker_key_OVER = bookmaker_key_OVER
        self.bookmaker_key_UNDER = bookmaker_key_UNDER
        self.odd_OVER = odd_OVER
        self.odd_UNDER = odd_UNDER
        self.profit = profit

    def __repr__(self):
        return f"Surebet(game_id={self.game_id}, outcome_id_OVER={self.outcome_id_OVER}, outcome_id_UNDER={self.outcome_id_UNDER}, bookmaker_key_OVER='{self.bookmaker_key_OVER}', bookmaker_key_UNDER='{self.bookmaker_key_UNDER}', odd_OVER={self.odd_OVER}, odd_UNDER={self.odd_UNDER}, profit={self.profit})"

    def __eq__(self, other):
        return self.game_id == other.game_id \
            and self.bookmaker_key_OVER == other.bookmaker_key_OVER \
            and self.bookmaker_key_UNDER == other.bookmaker_key_UNDER

    def __hash__(self):
        return hash((self.game_id, self.bookmaker_key_OVER, self.bookmaker_key_UNDER))

