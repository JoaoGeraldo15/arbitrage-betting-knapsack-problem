import os
import sys

from requests import Response

sys.path.append('/root/arbitrage-betting-knapsack-problem')
from src.service.game_service import GameService
import requests
from src.config.config import API_KEY, LAST_API_KEY_USED

if __name__ == '__main__':
    os.chdir('/root/arbitrage-betting-knapsack-problem')
    response = Response()
    response.status_code = 1
    amount_api_key = len(str(API_KEY).split(','))
    index_api_key = int(LAST_API_KEY_USED)
    while response.status_code != 200 and index_api_key != amount_api_key:
        key = f"{API_KEY.split(',')[index_api_key]}"
        URL = f'https://api.the-odds-api.com/v4/sports?apiKey={key}'
        response = requests.get(URL)
        index_api_key += 1

    if response.status_code == 200:
        data = response.json()
        leagues = [league['key'] for league in data if 'soccer_' in league['key']]

        if len(leagues):
            game_service = GameService()
            game_service.fetch_games(leagues)
