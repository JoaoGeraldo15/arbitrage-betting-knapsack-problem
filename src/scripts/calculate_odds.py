from collections import defaultdict
from typing import List

import pandas as pd

from src.model.models import Outcome, Game, Surebet
from src.repository.game_repository import GameRepository
from src.repository.outcome_repository import OutcomeRepository
from src.repository.surebet_repository import SurebetRepository


def obter_pontos(dataframe):
    odds_result = [i for i in dataframe.columns if 'totals' in i]
    totals_point = set(
        [float(i.replace('totals_OVER_', '').replace('totals_UNDER_', '').replace('_', '.')) for i in odds_result])
    totals_point = list(totals_point)
    totals_point.sort()
    return [str(i).replace('.', '_') for i in totals_point]


def obter_odd(opcao: str, outcomes: List[Outcome]) -> float:
    if outcomes[0].name == opcao:
        return outcomes[0].price
    elif outcomes[1].name == opcao:
        return outcomes[1].price
    else:
        return outcomes[2].price


# Função para calcular a diferença de tempo entre duas atualizações
def calcular_diferenca_tempo(atualizacao1, atualizacao2):
    return abs((atualizacao1 - atualizacao2).total_seconds() / 60) <= 15


# Função para gerar todas as combinações válidas
def combinacao_itens_valida(itens):
    combinacoes_validas = []

    for i in range(len(itens)):
        for j in range(i + 1, len(itens)):
            if itens[i].BOOKMAKER != itens[j].BOOKMAKER and calcular_diferenca_tempo(itens[i].update_time,
                                                                                     itens[j].update_time):
                combinacoes_validas.append((itens[i], itens[j]))

    return combinacoes_validas


def calcular_surebet(odd_1: float, odd_2: float) -> float:
    return (1 / odd_1) + (1 / odd_2)


def gerar_dataframe(result: List[Game]):
    registros = []
    linha = {}
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
                    key_df_1 = f"totals_{totals[0].name.upper()}_{str(totals[0].point).replace('.', '_')}"
                    key_df_2 = f"totals_{totals[1].name.upper()}_{str(totals[1].point).replace('.', '_')}"
                    linha[key_df_1] = (totals[0].id, totals[0].price)
                    linha[key_df_2] = (totals[1].id, totals[1].price)

                linha['update_time'] = update_time
                registros.append(linha)
    colunas = []
    for registro in registros:
        for i in registro.keys():
            if i not in colunas and i != 'update_time':
                colunas.append(i)
    colunas.append('update_time')
    return pd.DataFrame.from_records(registros, columns=colunas).fillna(0)


def obter_surebets(df_surebet: pd.DataFrame):
    arbitrages = []
    itens = [row for row in df_surebet.itertuples()]

    GAME_COLUMN = 1
    BOOKMAKER_COLUMN = 2
    UNDER_COLUMN = 3
    OVER_COLUMN = 4
    for item in combinacao_itens_valida(itens):
        odds_UNDER_A = item[0][UNDER_COLUMN][1]
        odds_OVER_A = item[0][OVER_COLUMN][1]

        odds_UNDER_B = item[1][UNDER_COLUMN][1]
        odds_OVER_B = item[1][OVER_COLUMN][1]

        arbitrage_1 = ((1 / odds_OVER_A) + (1 / odds_UNDER_B)) * 100
        arbitrage_2 = ((1 / odds_OVER_B) + (1 / odds_UNDER_A)) * 100
        game_id = item[0][GAME_COLUMN]
        if arbitrage_1 < 100:
            print(item)
            outcome_id_over = item[0][OVER_COLUMN][0]
            outcome_id_under = item[1][UNDER_COLUMN][0]
            bookmaker_over = item[0][BOOKMAKER_COLUMN]
            bookmaker_under = item[1][BOOKMAKER_COLUMN]
            profit = 100- arbitrage_1
            surebet = Surebet(game_id, outcome_id_over, outcome_id_under, bookmaker_over, bookmaker_under, odds_OVER_A,
                              odds_UNDER_B, profit)

            arbitrages.append(surebet)
            print(f'{round(arbitrage_1, 2)}% --> {item[0][OVER_COLUMN][0]} + {item[1][UNDER_COLUMN][0]}')

        if arbitrage_2 < 100:
            print(item)
            outcome_id_over = item[1][OVER_COLUMN][0]
            outcome_id_under = item[0][UNDER_COLUMN][0]
            bookmaker_over = item[1][BOOKMAKER_COLUMN]
            bookmaker_under = item[0][BOOKMAKER_COLUMN]
            profit = 100- arbitrage_2
            surebet = Surebet(game_id, outcome_id_over, outcome_id_under, bookmaker_over, bookmaker_under, odds_OVER_B,
                              odds_UNDER_A, profit)
            arbitrages.append(surebet)
            print(f'{round(arbitrage_2, 2)}% --> {item[1][OVER_COLUMN][0]} + {item[0][UNDER_COLUMN][0]}')

    return arbitrages


if __name__ == '__main__':
    outcome_repository = OutcomeRepository()
    surebet_repository = SurebetRepository()
    points = outcome_repository.find_all_points()
    game_repository = GameRepository()

    page_number = 1
    while True:
        print(page_number)
        games, restante = game_repository.find_paged(page_number, 50)
        if restante < 1:
            break
        page_number += 1
        df = gerar_dataframe(games)
        games_id = [i.id for i in games]

        surebet_list = []
        for id in games_id:
            # Itera por todos os mercados pegando um de cada vez
            pontos = obter_pontos(df.loc[df['GAME'] == id])
            for ponto in pontos:
                UNDER = f'totals_UNDER_{ponto}'
                OVER = f'totals_OVER_{ponto}'
                colunas = ['GAME', 'BOOKMAKER', UNDER, OVER, 'update_time']
                novo_df = df.loc[df['GAME'] == id][colunas].copy()
                colunas_drop = novo_df.columns[novo_df.eq('0').all() == True]
                novo_df.drop(colunas_drop, axis='columns', inplace=True)
                if len(novo_df.columns) == len(colunas):
                    novo_df = novo_df.loc[(novo_df[UNDER] != 0) & (novo_df[OVER] != 0)]
                    bookmakers = set(novo_df['BOOKMAKER'].to_list())
                    if len(bookmakers) > 1:
                        surebet_list.extend(obter_surebets(novo_df))

        surebet_repository.save_all(surebet_list)


