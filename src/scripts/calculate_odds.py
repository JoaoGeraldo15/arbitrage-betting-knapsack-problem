from collections import defaultdict
from typing import List

import pandas as pd

from src.model.models import Outcome
from src.repository.game_repository import GameRepository


def obter_odd(opcao: str, outcomes: List[Outcome]) -> float:
    if outcomes[0].name == opcao:
        return outcomes[0].price
    elif outcomes[1].name == opcao:
        return outcomes[1].price
    else:
        return outcomes[2].price


if __name__ == '__main__':
    repository = GameRepository()
    result = repository.find_paged(1, 1)
    i = 0
    registros = []
    linha = { }
    for game in result:
        for bookmaker in game.bookmakers:
            market_dict = defaultdict(list)
            outcome_dict = defaultdict(list)
            for market in bookmaker.markets:
                for outcome in market.outcomes:
                    outcome_dict[outcome.update_time].append((market.key, outcome))

            for key, value in outcome_dict.items():
                linha = {'GAME': game.id, 'BOOKMAKER': bookmaker.key.upper()}
                update_time = value[0][1].update_time
                totals = [item[1] for item in value if item[0] == 'totals']
                h2h = [item[1] for item in value if item[0] == 'h2h']

                if len(h2h) > 0:
                    key_df_1 = "h2h_HOME"
                    key_df_2 = "h2h_DRAW"
                    key_df_3 = "h2h_AWAY"
                    linha[key_df_1] = obter_odd(game.home_team, h2h)
                    linha[key_df_2] = obter_odd('Draw', h2h)
                    linha[key_df_3] = obter_odd(game.away_team, h2h)

                if len(totals) > 0:
                    key_df_1 = f"totals_{totals[0].name.upper()}_{totals[0].point}"
                    key_df_2 = f"totals_{totals[1].name.upper()}_{totals[1].point}"
                    linha[key_df_1] = totals[0].price
                    linha[key_df_2] = totals[1].price

                linha['update_time'] = update_time
                registros.append(linha)

    colunas = []
    for registro in registros:
        for i in registro.keys():
            if i not in colunas and i != 'update_time':
                colunas.append(i)

    colunas.append('update_time')

    df = pd.DataFrame.from_records(registros, columns=colunas)
    df = df.fillna(0)

    print(df.to_string())

# TODO para cada jogo criar uma view para facilitar o calculo, pegar a última atualização de cada jogo em cada bookmaker
# TODO para cada jogo comparar com os n-1(bookmakers-mercado) outros e verificar se possui a condição de surebet
# TODO criar uma tabela de resultados com as colunas (game_id, bookmaker_id_A, mercado_A, bookmaker_id_B, mercado_B, Lucro, %)
# TODO (game_id, outcome_A_under,outcome_B_over,  Lucro, %)
# TODO (game_id, outcome_A_over, outcome_B_under Lucro, %)
