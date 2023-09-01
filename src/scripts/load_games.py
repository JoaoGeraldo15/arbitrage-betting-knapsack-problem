import glob
import json
from typing import List

from src.schema import GameBase
from src.service.game_service import GameService


def get_single_game_list() -> List[GameBase]:
    json_files = glob.glob("../data/single_game/*.json")
    QUOTA_REACHED_KEY = 'message'
    games = list()
    for arq in json_files:
        with open(arq, "r") as file:
            data = json.load(file)
        if QUOTA_REACHED_KEY in data:
            continue
        games.append(GameBase(**data))
    return games


def get_game_list() -> List[GameBase]:
    games = list()
    json_files = glob.glob("../data/games/*.json")
    for arq in json_files:
        with open(arq, "r") as file:
            data = json.load(file)
        games = [GameBase(**game) for game in data[0]]
    return games


if __name__ == '__main__':
    service = GameService()
    games = get_game_list()
    games.extend(get_single_game_list())
    count = 0
    data = list()
    for game in games:
        data.append((count, game))
        count += 1

    while data:
        games_to_save: List[GameBase] = []
        list_id_games = []
        for tupla in data:
            if tupla[1].id not in [i[1].id for i in list_id_games]:
                list_id_games.append(tupla)
                games_to_save.append(tupla[1])

        selecionados = [tupla[0] for tupla in list_id_games]
        data = [tupla for tupla in data if tupla[0] not in selecionados]

        service.save_games(games_to_save)
        print(len(data))
