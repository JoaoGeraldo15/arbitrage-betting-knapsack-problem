import os

import sys
import time

from requests import Response

sys.path.append('/root/arbitrage-betting-knapsack-problem')
import json
import sys
import uuid
from datetime import datetime, date
import requests
from src.config.config import API_KEY
from src.schema import GameBase
from src.service.game_service import GameService
from src.util import checkout_root_path, replace_api_key

if __name__ == '__main__':
    os.chdir('/root/arbitrage-betting-knapsack-problem')
    game_id = sys.argv[1]
    sport = sys.argv[2]

    params = {
        'apiKey': API_KEY.split(',')[0],
        'region': 'eu',
        'markets': 'totals,btts,draw_no_bet',
        'bookmakers': 'betfair,betsson,matchbook,pinnacle,williamhill,sport888,onexbet,betonlineag,unibet_eu,nordicbet'
    }

    URL_ODDS = f'https://api.the-odds-api.com/v4/sports/{sport}/events/{game_id}/odds'
    odds_response = Response()
    odds_response.status_code = 1
    while odds_response.status_code != 200:
        odds_response = requests.get(url=URL_ODDS, params=params)
        if odds_response.status_code == 401 or int(odds_response.headers['X-Requests-Remaining']) < 30:
            replace_api_key(params['apiKey'])
            time.sleep(1.5)
            params['apiKey'] = API_KEY.split(',')[1]

    log = f"[API_KEY]: {params['apiKey']} \n[Requests-Used]: {odds_response.headers['X-Requests-Used']} \n[Requests-Remaining]: {odds_response.headers['X-Requests-Remaining']} \n[Date]: {odds_response.headers['Date']}"
    with open('log/log_jogos', 'w') as f:
        f.write(log)

    file_name = f"{date.today().strftime('%d_%m_%Y')}_[{datetime.now().strftime('%H:%M:%S')}]_{str(uuid.uuid4())}.json"
    with open(f"src/data/single_game/{file_name}", "w") as f:
        json.dump(odds_response.json(), f)

    service = GameService()
    game = GameBase(**odds_response.json())
    service.save_games([game])







