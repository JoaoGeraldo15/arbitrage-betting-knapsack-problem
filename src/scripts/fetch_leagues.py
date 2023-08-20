import sys
sys.path.append('/root/arbitrage-betting-knapsack-problem')
from src.service.game_service import GameService
from src.util import checkout_root_path
import requests
from src.config.config import API_KEY


if __name__ == '__main__':
    checkout_root_path()
    key = f"{API_KEY.split(',')[0]}"
    URL = f'https://api.the-odds-api.com/v4/sports?apiKey={key}'
    print(key)
    response = requests.get(URL)
    print(response)
    data = response.json()
    leagues = [league['key'] for league in data if 'soccer_' in league['key']]

    if len(leagues):
        print(leagues)
        game_service = GameService()
        game_service.fetch_games(leagues)
