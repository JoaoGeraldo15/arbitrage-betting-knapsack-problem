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
            linha = {'GAME': game.id, 'BOOKMAKER': bookmaker.key.upper()}
            market_dict = defaultdict(list)
            for market in bookmaker.markets:
                outcome_dict = defaultdict(list)
                for outcome in market.outcomes:
                    outcome_dict[outcome.update_time].append(outcome)

                for key, value in outcome_dict.items():
                    if market.key == 'totals':
                        key_df_1 = f"{market.key}_{value[0].name.upper()}_{value[0].point}"
                        key_df_2 = f"{market.key}_{value[1].name.upper()}_{value[1].point}"
                        linha[key_df_1] = value[0].price
                        linha[key_df_2] = value[1].price
                    elif market.key == 'h2h':
                        key_df_1 = f"{market.key}_HOME"
                        key_df_2 = f"{market.key}_DRAW"
                        key_df_3 = f"{market.key}_AWAY"
                        linha[key_df_1] = obter_odd(game.home_team, value)
                        linha[key_df_2] = obter_odd('Draw', value)
                        linha[key_df_3] = obter_odd(game.away_team, value)

                    linha['update_time'] = value[0].update_time
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
