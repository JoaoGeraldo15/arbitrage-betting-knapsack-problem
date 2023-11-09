import time
import uuid

from tqdm import tqdm
from src.genetic.arbitrage import CrossOverEnum, Population
from src.repository.surebet_repository import SurebetRepository
from src.util import ExportadorDeGraficos
from itertools import product
import random
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'


def assign_ranking(df):
    largest = df['Hypervolume'].nlargest(2)
    smallest = df['Hypervolume'].nsmallest(2)

    df['rank_column'] = 0  # Inicialize a coluna com 0

    df.loc[largest.index[0], 'rank_column'] = 1
    df.loc[largest.index[1], 'rank_column'] = 2
    df.loc[smallest.index[1], 'rank_column'] = 15
    df.loc[smallest.index[0], 'rank_column'] = 16


def fatorial_2k(crossover, filename, callback_config, arbitrages):
    export = ExportadorDeGraficos()
    n_generations, n_individuals, mutation_rate, crossover_rate = callback_config()
    parametros = list(product(n_generations, n_individuals, mutation_rate, crossover_rate))
    simulations = []
    iteracoes = list()
    for i in range(0, 10):
        iteracoes.extend(parametros)

    random.shuffle(iteracoes)

    dataframe = pd.DataFrame(
        columns=['Generations', 'Individuals', 'Mutation Rate', 'Crossover Rate', 'Hypervolume', 'Execution Time'])
    dataframes = []
    print(filename)
    barra_progresso = tqdm(total=len(iteracoes), unit="itens")

    for i in iteracoes:
        start_time = time.time()
        population = Population(n_generations=i[0], n_individuals=i[1], mutation_rate=i[2], crossover_rate=i[3],
                                budget=100, crossover_strategy=crossover, arbitrages=arbitrages)
        simulations.append(population)
        end_time = time.time()
        hypervolume = export.get_max_hypervolume(population)
        execution_time = (end_time - start_time) * 1000  # millisegundos

        data = {
            'Generations': i[0],
            'Individuals': i[1],
            'Mutation Rate': i[2],
            'Crossover Rate': i[3],
            'Hypervolume': hypervolume,
            'Execution Time': execution_time
        }
        temp_df = pd.DataFrame([data])
        dataframes.append(temp_df)

        barra_progresso.update(1)
    barra_progresso.close()
    dataframe = pd.concat(dataframes, ignore_index=True)
    dataframe.to_csv(f"{filename}.csv", index=False)

    result = dataframe.groupby(['Generations', 'Individuals', 'Mutation Rate', 'Crossover Rate'])[
        ['Hypervolume', 'Execution Time']].median().reset_index()

    # Invertendo o dataframe
    dataframe_invertido = result.iloc[::-1]

    assign_ranking(dataframe_invertido)

    # Exporta para csv a mediana dos testes
    dataframe_invertido.to_csv(f"{filename}_median.csv", index=False)

    export.hypervolume_plots(simulations, crossover.name)


def config_fatorial_2k_v1() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [200, 100]
    n_individuals = [100, 50]
    mutation_rate = [0.05, 0.03]
    crossover_rate = [1, 0.95]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_v2() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [150, 30]
    n_individuals = [50, 25]
    mutation_rate = [0.02, 0.01]
    crossover_rate = [0.95, 0.85]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_one_point_v2() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [220, 120]
    n_individuals = [80, 30]
    mutation_rate = [0.02, 0.04]
    crossover_rate = [1.0, 0.95]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_one_point_v3() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [240, 140]
    n_individuals = [50, 20]
    mutation_rate = [0.02, 0.01]
    crossover_rate = [0.95]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_one_point_v4() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [300, 100]
    n_individuals = [50, 20]
    mutation_rate = [0.05, 0.01]
    crossover_rate = [1, 0.95]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_v3() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [120, 75]
    n_individuals = [35, 20]
    mutation_rate = [0.02, 0.01]
    crossover_rate = [1.0, 0.95]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_two_points_v2() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [180, 120]
    n_individuals = [80, 30]
    mutation_rate = [0.02, 0.04]
    crossover_rate = [1.0, 0.95]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_two_points_v3() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [160, 140]
    n_individuals = [60, 20]
    mutation_rate = [0.04, 0.03]
    crossover_rate = [1.0, 0.95]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_two_points_v4() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [180, 160]
    n_individuals = [40, 20]
    mutation_rate = [0.03, 0.02]
    crossover_rate = [1.0, 0.95]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def projeto_fatorial_one_point(arbitrages):
    crossover = CrossOverEnum.ONE_POINT_CROSSOVER
    fatorial_2k(crossover, crossover.name + "_fatorial_v1", config_fatorial_2k_v1, arbitrages)
    fatorial_2k(crossover, crossover.name + "_fatorial_v2", config_fatorial_2k_one_point_v2, arbitrages)
    fatorial_2k(crossover, crossover.name + "_fatorial_v3", config_fatorial_2k_one_point_v3, arbitrages)
    fatorial_2k(crossover, crossover.name + f"_fatorial_{str(uuid.uuid4())[:10]}", config_fatorial_2k_one_point_v4, arbitrages)


def projeto_fatorial_two_points(arbitrages):
    crossover = CrossOverEnum.TWO_POINT_CROSSOVER
    fatorial_2k(crossover, crossover.name + "_fatorial_v1", config_fatorial_2k_v1, arbitrages)
    fatorial_2k(crossover, crossover.name + "_fatorial_v2", config_fatorial_2k_two_points_v2, arbitrages)
    fatorial_2k(crossover, crossover.name + "_fatorial_v3", config_fatorial_2k_two_points_v3, arbitrages)


def config_fatorial_2k_uniform_points_v2() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [220, 120]
    n_individuals = [80, 30]
    mutation_rate = [0.02, 0.04]
    crossover_rate = [1.0, 0.95]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_uniform_points_v3() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [240, 140]
    n_individuals = [60, 20]
    mutation_rate = [0.04, 0.03]
    crossover_rate = [1.0, 0.95]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_uniform_points_v4() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [160, 100]
    n_individuals = [30, 15]
    mutation_rate = [0.02, 0.005]
    crossover_rate = [0.95, 0.75]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def projeto_fatorial_uniform_points(arbitrages):
    crossover = CrossOverEnum.UNIFORM_CROSSOVER
    fatorial_2k(crossover, crossover.name + "_fatorial_v1", config_fatorial_2k_v1, arbitrages)
    fatorial_2k(crossover, crossover.name + "_fatorial_v2", config_fatorial_2k_uniform_points_v2, arbitrages)
    fatorial_2k(crossover, crossover.name + "_fatorial_v3", config_fatorial_2k_uniform_points_v3, arbitrages)


if __name__ == '__main__':
    repository = SurebetRepository()
    start_date = '2023-09-01 19:00:00'
    end_date = '2023-09-01 20:00:00'
    arbitrages = repository.find_all_unique_between(start_date, end_date)

    projeto_fatorial_one_point(arbitrages)
    projeto_fatorial_two_points(arbitrages)
    projeto_fatorial_uniform_points(arbitrages)