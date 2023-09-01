import os
import subprocess
from datetime import datetime, timedelta

from injectable import injectable


@injectable
class AtTaskService():
    def do(self, script_path:str, param1: str, param2:str, date: str):
        cmd = f"echo '/root/arbitrage-betting-knapsack-problem/venv/bin/python3 {script_path} {param1} {param2}' | at {date}"
        os.system(f"echo cmd: '{cmd}' >> at_log.txt")
        subprocess.run(cmd, shell=True)

#if __name__ == '__main__':
#    service = AtTaskService()
#    path = '/root/arbitrage-betting-knapsack-problem/src/scripts/fetch_single_game.py'
#    param1 = '5b115b8073519596bb4bbdbbcabdb4c9'
#    param2 = 'soccer_brazil_campeonao'
#    data = (datetime.now() + timedelta(minutes=2)).strftime("%H:%M %Y-%m-%d")
#    service.do(path, param1, param2, data)
