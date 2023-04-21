import json
import sys
import uuid
from datetime import datetime, date

import requests

from src.config.config import API_KEY
from src.service.game_service import GameService

if __name__ == '__main__':
    game_id = sys.argv[1]
    sport = sys.argv[2]


    params = {
        'apiKey': API_KEY,
        'region': 'eu',
        'markets': 'totals,btts,draw_no_bet',
        'bookmakers': 'betfair,betsson,matchbook,pinnacle,williamhill,sport888,onexbet,betonlineag,unibet_eu,nordicbet'
    }

    URL_ODDS = f'https://api.the-odds-api.com/v4/sports/{sport}/events/{game_id}/odds'
    odds_response = requests.get(url=URL_ODDS, params=params)

    log = f"[Requests-Used]: {odds_response.headers['X-Requests-Used']} \n[Requests-Remaining]: {odds_response.headers['X-Requests-Remaining']} \n[Date]: {odds_response.headers['Date']}"
    with open('../../log/log_jogos', 'w') as f:
        f.write(log)

    file_name = f"{date.today().strftime('%d_%m_%Y')}_[{datetime.now().strftime('%H:%M:%S')}]_{str(uuid.uuid4())}.json"
    with open(f"../data/single_game/{file_name}", "w") as f:
        json.dump(odds_response.json(), f)

    service = GameService()
    service.save_games(odds_response.json())







