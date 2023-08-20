import os

from src.config.config import API_KEY


def checkout_root_path():
    # Altera o diretório de trabalho atual para o diretório raiz do código
    os.chdir('/root/arbitrage-betting-knapsack-problem')


def replace_api_key(api_key):
    file_path = 'arbitrage-betting-knapsack-problem/.env'
    keys = API_KEY.split(',')
    new_api_key = ','.join([key for key in keys if key not in api_key])

    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if line.startswith("API_KEY="):
                line = f"API_KEY={new_api_key}\n"
            file.write(line)
