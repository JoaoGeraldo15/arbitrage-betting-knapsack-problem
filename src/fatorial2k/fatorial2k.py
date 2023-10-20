import time

from src.genetic.arbitrage import CrossOverEnum, Population
from src.repository.surebet_repository import SurebetRepository
from src.util import ExportadorDeGraficos
from itertools import product
import random
import pandas as pd


def fatorial_2k(crossover, export: ExportadorDeGraficos, filename, callback_config):
    n_generations, n_individuals, mutation_rate, crossover_rate = callback_config()
    parametros = list(product(n_generations, n_individuals, mutation_rate, crossover_rate))
    simulations = []
    iteracoes = list()
    for i in range(0, 10):
        iteracoes.extend(parametros)

    random.shuffle(iteracoes)
    print(len(iteracoes))

    dataframe = pd.DataFrame(
        columns=['Generations', 'Individuals', 'Mutation Rate', 'Crossover Rate', 'Hypervolume', 'Execution Time'])
    dataframes = []
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
    dataframe = pd.concat(dataframes, ignore_index=True)
    dataframe.to_csv(f"{filename}.csv", index=False)

    # Calculando a média de todos os 10 testes
    result = dataframe.groupby(['Generations', 'Individuals', 'Mutation Rate', 'Crossover Rate']).agg(
        {'Hypervolume': 'mean', 'Execution Time': 'mean'}).reset_index()

    # Invertendo o dataframe
    dataframe_invertido = result.iloc[::-1]

    # Exporta para csv a media dos testes
    dataframe_invertido.to_csv(f"{filename}_average.csv", index=False)

    export.hypervolume_plots(simulations, crossover.name)


def config_fatorial_2k_v1() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [100, 50]
    n_individuals = [100, 50]
    mutation_rate = [0.05, 0.01]
    crossover_rate = [1, 0.8]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_v2() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [150, 30]
    n_individuals = [50, 25]
    mutation_rate = [0.02, 0.01]
    crossover_rate = [0.95, 0.85]

    return n_generations, n_individuals, mutation_rate, crossover_rate


def config_fatorial_2k_v3() -> tuple[list[int], list[int], list[float], list[float]]:
    n_generations = [120, 75]
    n_individuals = [35, 20]
    mutation_rate = [0.02, 0.01]
    crossover_rate = [1.0, 0.95]

    return n_generations, n_individuals, mutation_rate, crossover_rate


if __name__ == '__main__':
    repository = SurebetRepository()
    start_date = '2023-09-01 19:55:00'
    end_date = '2023-09-01 20:00:00'
    arbitrages = repository.find_all_unique_between(start_date, end_date)
    crossover = CrossOverEnum.UNIFORM_CROSSOVER_ONE_INDIVIDUAL
    export = ExportadorDeGraficos()
    fatorial_2k(crossover, export, "fatorial_v1", config_fatorial_2k_v1)
    fatorial_2k(crossover, export, "fatorial_v2", config_fatorial_2k_v2)
    fatorial_2k(crossover, export, "fatorial_v3", config_fatorial_2k_v3)
