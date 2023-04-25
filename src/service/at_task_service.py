import subprocess
from datetime import datetime, timedelta

from injectable import injectable


@injectable
class AtTaskService():
    def do(self, script_path:str, param1: str, param2:str, date: str):
        cmd = f"echo 'arbitrage-betting-knapsack-problem/venv/bin/python3 {script_path} {param1} {param2}' | at {date}"
        subprocess.run(cmd, shell=True)

if __name__ == '__main__':
    service = AtTaskService()
    path = '/root/arbitrage-betting-knapsack-problem/src/scripts/fetch_single_game.py'
    param1 = '9320459d969fc583e38fb030402f82bd'
    param2 = 'soccer_spain_la_liga'
    data = (datetime.now() + timedelta(minutes=2)).strftime("%H:%M %Y-%m-%d")
    service.do(path, param1, param2, data)
