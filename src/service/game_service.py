import json
import os
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, date, timezone, timedelta
from typing import List

import pytz
import requests
from injectable import autowired, Autowired
from requests import Response

from src.config.config import API_KEY, LAST_API_KEY_USED
from src.model.models import Game, Bookmaker, Market, Outcome
from src.repository.game_repository import GameRepository
from src.schema.schema import GameBase
from src.service.at_task_service import AtTaskService
from src.config.config import SCRIPTS_PATH
from src.util import replace_api_key
import glob


class GameService:
    @autowired
    def __init__(self, repository: Autowired(GameRepository), at: Autowired(AtTaskService)):
        self.repository = repository
        self.at = at

    def get_games(self):
        return self.repository.find_all()

    def __get_game_saved(self, game_id: str, game_list: List[Game]) -> Game | None:
        try:
            return [game for game in game_list if game.id == game_id][0]
        except:
            return None

    def __get_bookmaker_if_exist(self, key: str, bookmaker_list: List[Bookmaker]) -> Bookmaker | None:
        try:
            return [bookmaker for bookmaker in bookmaker_list if bookmaker.key == key][0]
        except:
            return None

    def __get_market_if_exist(self, key: str, markets: List[Market]) -> Market | None:
        try:
            return [market for market in markets if market.key == key][0]
        except:
            return None

    def save_game_first(self, games: List[GameBase]):
        games_only = list()
        for game in games:
            game.bookmakers = list()
            games_only.append(Game.from_schema(game))

        self.repository.save_all(games_only)

    @contextmanager
    def save_games(self, games: List[GameBase]):
        # Pega os ids dos jogos
        games_id = [game.id for game in games]

        # Busca no banco todos os jogos com os ids especificados
        games_saved: List[Game] = self.repository.find_all_by_id(games_id)

        # Recupera os ids dos jogos já registrados
        game_saved_ids: List[str] = [jogo.id for jogo in games_saved]

        # Separa em uma lista os jogos que não foram salvos
        new_games = [Game.from_schema(dto) for dto in games if dto.id not in game_saved_ids]

        # Atualiza os jogos que já estão salvos
        updatable_games = [Game.from_schema(dto) for dto in games if dto.id in game_saved_ids]
        data_updated = False
        updated_games = []
        for game in updatable_games:
            data_updated = False
            game_saved = self.__get_game_saved(game.id, games_saved)
            for bookmaker in game.bookmakers:
                bookmaker_saved = self.__get_bookmaker_if_exist(bookmaker.key, game_saved.bookmakers)
                if bookmaker_saved is not None:
                    for market in bookmaker.markets:
                        market_saved = self.__get_market_if_exist(market.key, bookmaker_saved.markets)
                        if market_saved is not None:
                            if len([o for o in market.outcomes if o not in set(market_saved.outcomes)]):
                                for outcome in market.outcomes:
                                    new_outcome = Outcome(name=outcome.name, price=outcome.price, point=outcome.point,
                                                          update_time=outcome.update_time, market_id=market_saved.id)
                                    market_saved.outcomes.append(new_outcome)
                                data_updated = True
                        else:
                            # Não existe o Market, então só basta adicionar no bookmaker
                            new_market = Market(key=market.key, last_update=market.last_update,
                                                outcomes=market.outcomes, bookmaker_id=bookmaker_saved.id)
                            bookmaker_saved.markets.append(new_market)
                            data_updated = True

                else:
                    # Bookmaker não existe, basta salvar o novo bookmaker
                    new_bookmaker = Bookmaker(key=bookmaker.key, title=bookmaker.title,
                                              last_update=bookmaker.last_update, markets=bookmaker.markets,
                                              game_id=game_saved.id)
                    game_saved.bookmakers.append(new_bookmaker)
                    data_updated = True

            if data_updated:
                updated_games.append(game_saved)

        if len(new_games):
            games_saved.extend(new_games)
            self.repository.save_all(new_games)

        if len(updated_games):
            self.repository.save_all(updated_games)

    def fetch_games(self, leagues: List[str]):
        params = {
            'apiKey': API_KEY.split(',')[0],
            'region': 'eu',
            'markets': 'totals,h2h',
            'bookmakers': 'betfair,betsson,matchbook,pinnacle,williamhill,sport888,onexbet,betonlineag,unibet_eu,nordicbet'
        }

        response_list = []
        response = Response()
        response.status_code = 1
        games = []
        amount_api_key = len(API_KEY.split(','))
        index_api_key = int(LAST_API_KEY_USED)
        os.system(f"echo index_api_key: '{index_api_key}' amount_api_key: '{amount_api_key}' >> ../fetch_leagues.txt")
        for league in leagues:
            while response.status_code != 200 and index_api_key != amount_api_key:
                URL = f'https://api.the-odds-api.com/v4/sports/{league}/odds/'
                response = requests.get(url=URL, params=params)
                if response.status_code == 401 or int(response.headers['X-Requests-Remaining']) < 30:
                    time.sleep(1.5)
                    index_api_key += 1
                    params['apiKey'] = API_KEY.split(',')[index_api_key]
                    continue
                games.extend(response.json())
                response_list.append(response.json())
                time.sleep(1.5)
            response.status_code = 1

        os.system(f"echo antes' >> ../fetch_leagues.txt")
        self.atualizarApiKeyUsada(index_api_key)
        os.system(f"echo depois' >> ../fetch_leagues.txt")

        log = f"[API_KEY]: {params['apiKey']} \n[Requests-Used]: {response.headers['X-Requests-Used']} \n[Requests-Remaining]: {response.headers['X-Requests-Remaining']} \n[Date]: {response.headers['Date']}"
        with open('log/log_jogos', 'w') as f:
            f.write(log)

        file_name = f"{date.today().strftime('%d_%m_%Y')}_[{datetime.now().strftime('%H:%M:%S')}]_{str(uuid.uuid4())}.json"
        with open(f"src/data/games/{file_name}", "w") as f:
            json.dump(response_list, f)

        games = [GameBase(**game) for game in games]

        try:
            self.save_games(games)
        except Exception as e:
            os.system(f"echo '{e}' >> error_save_games.txt")

        games_to_schedule = [g for g in games if g.commence_time.date() == datetime.now(timezone.utc).date()]
        path = f'{SCRIPTS_PATH}/fetch_single_game.py'
        sp_zone = pytz.timezone('America/Sao_Paulo')
        for g in games_to_schedule:
            schedule_time_1 = (g.commence_time.astimezone(sp_zone) - timedelta(minutes=150)).strftime("%H:%M %Y-%m-%d")
            schedule_time_2 = (g.commence_time.astimezone(sp_zone) - timedelta(minutes=60)).strftime("%H:%M %Y-%m-%d")
            schedule_time_3 = (g.commence_time.astimezone(sp_zone) - timedelta(minutes=30)).strftime("%H:%M %Y-%m-%d")
            schedule_time_4 = (g.commence_time.astimezone(sp_zone) - timedelta(minutes=-30)).strftime("%H:%M %Y-%m-%d")
            schedule_time_5 = (g.commence_time.astimezone(sp_zone) - timedelta(minutes=-60)).strftime("%H:%M %Y-%m-%d")
            self.at.do(path, g.id, g.sport_key, schedule_time_1)
            self.at.do(path, g.id, g.sport_key, schedule_time_2)
            self.at.do(path, g.id, g.sport_key, schedule_time_3)
            self.at.do(path, g.id, g.sport_key, schedule_time_4)
            self.at.do(path, g.id, g.sport_key, schedule_time_5)

    def atualizarApiKeyUsada(self, index_api_key):
        with open(".env", "r") as file:
            lines = file.readlines()
        with open(".env", "w") as file:
            for line in lines:
                if line.startswith("LAST_API_KEY_USED="):
                    line = f"LAST_API_KEY_USED={index_api_key}\n"
                file.write(line)


