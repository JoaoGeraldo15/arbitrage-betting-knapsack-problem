import math
import pickle
import random
from enum import Enum
from typing import List

import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
import datetime
import pygmo as pg

from src.repository.surebet_repository import SurebetRepository
from src.util import ExportadorDeGraficos


class CrossOverEnum(Enum):
    UNIFORM_CROSSOVER = 1
    UNIFORM_CROSSOVER_ONE_INDIVIDUAL = 2
    ONE_POINT_CROSSOVER = 3
    TWO_POINT_CROSSOVER = 4


class Arbitrage:
    # def __init__(self, game_id, outcome_id_OVER, outcome_id_UNDER, bookmaker_key_OVER,
    # bookmaker_key_UNDER, odd_OVER, odd_UNDER, last_update_OVER, last_update_UNDER, profit):
    def __init__(self, game_id, outcome_id_OVER, outcome_id_UNDER, bookmaker_key_OVER,
                 bookmaker_key_UNDER, odd_OVER, odd_UNDER, profit):
        self.game_id = game_id
        self.outcome_id_OVER = outcome_id_OVER
        self.outcome_id_UNDER = outcome_id_UNDER
        self.bookmaker_key_OVER = bookmaker_key_OVER
        self.bookmaker_key_UNDER = bookmaker_key_UNDER
        self.odd_OVER = odd_OVER
        self.odd_UNDER = odd_UNDER
        self.last_update_OVER = 1
        self.last_update_UNDER = 1
        self.profit = profit

    def __eq__(self, other) -> bool:
        return self.game_id == other.game_id \
            and self.outcome_id_OVER == other.outcome_id_OVER \
            and self.outcome_id_UNDER == other.outcome_id_UNDER \
            and self.odd_OVER == other.odd_OVER \
            and self.odd_UNDER == other.odd_UNDER

    def __hash__(self) -> int:
        return hash((self.game_id, self.outcome_id_OVER, self.outcome_id_UNDER, self.odd_OVER, self.odd_UNDER))


class Individual:
    def __init__(self, arbitrages, budget, geracao=0, init_population=False):
        self.arbitrages = arbitrages
        self.profits = [i.profit for i in arbitrages]
        self.budget = budget
        self.geracao = geracao
        self.fitness = []
        self.fitness_normalized = []
        self.fitness_max_profit = None
        self.fitness_diversification = None
        self.chromosome: list[tuple[int, float]] = []
        self.dominated_by = []  # Lista de soluções que dominam esta solução
        self.dominated_solutions = []  # Lista de soluções que esta solução domina
        self.dominated_by_count = 0  # Por quantas soluções esta solução é dominada
        self.rank = None  # Rank da solução nas frentes de Pareto
        self.crowding_distance = None  # Distância de lotação da solução

        if init_population:
            self.initialize_individual(arbitrages)

    def initialize_individual(self, arbitrages):
        total_profit = 0
        count_profit = 0
        for i in range(len(arbitrages)):
            valor = round(random.random(), 2)
            if valor < 0.5:
                self.chromosome.append((0, valor))
            else:
                self.chromosome.append((1, valor))
                total_profit += self.profits[i]
                count_profit += 1
        self.normalize_budget_allocation()
        self.evaluate_fitness()

    def normalize_budget_allocation(self):
        total = sum([chromosome[1] for chromosome in self.chromosome if chromosome[0] == 1])
        if total == 0:
            return

        for index in range(len(self.chromosome)):
            chromosome = self.chromosome[index]
            if chromosome[0] == 1:
                new_value_normalized = round(chromosome[1] / total, 2)
                self.chromosome[index] = (1, new_value_normalized)

    def objective_function_max_profit(self):
        fit = 0
        for index in range(len(self.chromosome)):
            gene = self.chromosome[index]
            if gene[0] == 1:
                fit += round(self.profits[index] * (gene[1] * self.budget), 2)
        self.fitness_max_profit = fit
        self.fitness.append(fit)

    def objective_function_diversification(self):
        entropy = 0
        for index in range(len(self.chromosome)):
            gene = self.chromosome[index]
            if gene[0] == 1 and gene[1] > 0:
                entropy -= gene[1] * math.log2(gene[1])

        self.fitness_diversification = entropy
        self.fitness.append(entropy)

    def evaluate_fitness(self):
        self.fitness = []
        self.objective_function_max_profit()
        self.objective_function_diversification()

    def normalize_fitness(self, highest_fitness):
        num_objectives = len(self.fitness)
        for obj_index in range(num_objectives):
            fit = highest_fitness[obj_index]
            self.fitness_normalized.append(round(self.fitness[obj_index] / fit, 4))

    def print_chromossome(self):
        print(f'{self.chromosome} --> {self.fitness} --> {self.fitness_normalized}')


class Population:
    def __init__(self, arbitrages, n_individuals, budget, crossover_strategy: CrossOverEnum, mutation_rate,
                 n_generations=10):
        """
        Inicializa a população de soluções no contexto do algoritmo NSGA-II.

        Args:
            num_individuals (int): O número de indivíduos na população.
            arbitrages (list): É uma lista de objetos Arbitrage representando as oportunidades de arbitragem.
            budget (float): Orçamento disponível para alocação nas apostas.
        """

        self.crossover_strategy = crossover_strategy
        self.n_individuals = n_individuals
        self.solutions: List[Individual] = []  # Lista de todas as soluções
        self.step_solutions: List[Individual] = []  # Lista auxiliar que será usada para construir a geração de filhos
        self.high_fitness_evaluated = [0, 0]
        self.pareto_fronts = []  # Lista de listas representando as frentes de Pareto
        self.solutions_history: List = []
        self.pareto_history_front = []
        self.pareto_history_front_normalized = []
        self.n_generations = n_generations
        self.generation = 0
        self.mutation_rate = mutation_rate

        for _ in range(self.n_individuals):
            individual = Individual(arbitrages, budget, init_population=True)
            self.solutions.append(individual)

        self.__main()

    def __main(self):
        # self.__normalize_fitness_population(self.solutions)
        self.__nsga_evaluation()
        self.__commit_history_solutions()
        self.generation += 1

        # Selecionar os pais e realizar cruzamento, mutação até ter uma população 2N
        while self.generation < self.n_generations:
            self.step_solutions = []
            while len(self.step_solutions) < self.n_individuals:  # Gerando os filhos
                self.__evolve(self.crossover_strategy, self.__tournament_selection(), self.__tournament_selection())
                # self.__evolve(self.crossover_strategy, self.__roulette_selection(), self.__roulette_selection())
            # self.__normalize_fitness_population(self.step_solutions)
            self.solutions.extend(self.step_solutions[: self.n_individuals])
            self.__nsga_evaluation()
            self.__select_survivors()
            self.__commit_history_solutions()
            self.generation += 1

        self.__normalize_fitness()

        self.export_solutions()

    def __evolve(self, enum: CrossOverEnum, parent_1: Individual, parent_2: Individual):
        childes: List[Individual] = []
        if enum.value == CrossOverEnum.UNIFORM_CROSSOVER:
            childes = self.__uniform_crossover(parent_1, parent_2)
        elif enum.value == CrossOverEnum.UNIFORM_CROSSOVER_ONE_INDIVIDUAL:
            childes = [self.__uniform_crossover_one_individual(parent_1, parent_2)]
        elif enum.value == CrossOverEnum.UNIFORM_CROSSOVER_ONE_INDIVIDUAL:
            childes = self.__one_point_crossover(parent_1, parent_2)
        else:
            childes = self.__two_point_crossover(parent_1, parent_2)

        for child in childes:
            # if random.random() < 0.2:
            if random.random() < self.mutation_rate:
                self.__mutation(child)

    def __tournament_selection(self) -> Individual:
        tournament = random.sample(self.solutions, 2)
        tournament.sort(key=lambda x: (x.rank, -x.crowding_distance))
        return tournament[0]

    def __roulette_selection(self) -> Individual:
        total_crowding_distance = sum([i.crowding_distance for i in self.solutions])

        # Gera um número aleatório entre 0 e total_crowding_distance
        random_number = random.uniform(0, total_crowding_distance)

        pointer = 0

        for i in self.solutions:
            pointer += i.crowding_distance
            if pointer >= random_number:
                return i

    def __mutation(self, child: Individual):
        random_index = random.randrange(len(child.chromosome))
        if child.chromosome[random_index][0] == 1:
            child.chromosome[random_index] = (0, child.chromosome[random_index][1])
        else:
            child.chromosome[random_index] = (1, child.chromosome[random_index][1])

        child.normalize_budget_allocation()
        child.evaluate_fitness()

    def __uniform_crossover(self, parent_1: Individual, parent_2: Individual) -> List[Individual]:
        child_1 = Individual(parent_1.arbitrages, parent_1.budget)
        child_2 = Individual(parent_1.arbitrages, parent_1.budget)

        for gene_parent_1, gene_parent_2 in zip(parent_1.chromosome, parent_2.chromosome):
            if random.random() < 0.5:  # 50% de chance de herdar do parent_1
                child_1.chromosome.append(gene_parent_1)
                child_2.chromosome.append(gene_parent_2)
            else:  # 50% de chance de herdar do parent_2
                child_1.chromosome.append(gene_parent_2)
                child_2.chromosome.append(gene_parent_1)

        child_1.normalize_budget_allocation()
        child_2.normalize_budget_allocation()
        child_1.evaluate_fitness()
        child_2.evaluate_fitness()
        self.step_solutions.extend([child_1, child_2])
        return [child_1, child_2]

    def __uniform_crossover_one_individual(self, parent_1: Individual, parent_2: Individual) -> Individual:
        child = Individual(parent_1.arbitrages, parent_1.budget)

        for gene_parent_1, gene_parent_2 in zip(parent_1.chromosome, parent_2.chromosome):
            if random.random() < 0.5:  # 50% de chance de herdar do parent_1
                child.chromosome.append(gene_parent_1)
            else:  # 50% de chance de herdar do parent_2
                child.chromosome.append(gene_parent_2)

        child.normalize_budget_allocation()
        child.evaluate_fitness()
        self.step_solutions.append(child)
        return child

    def __one_point_crossover(self, parent_1: Individual, parent_2: Individual) -> List[Individual]:
        cut_point_crossover = random.randrange(len(parent_1.chromosome))

        child_1_chromosome = parent_1.chromosome[:cut_point_crossover] + parent_2.chromosome[cut_point_crossover:]
        child_2_chromosome = parent_2.chromosome[:cut_point_crossover] + parent_1.chromosome[cut_point_crossover:]

        child_1 = Individual(parent_1.arbitrages, parent_1.budget)
        child_2 = Individual(parent_1.arbitrages, parent_1.budget)

        child_1.chromosome = child_1_chromosome
        child_2.chromosome = child_2_chromosome
        child_1.normalize_budget_allocation()
        child_2.normalize_budget_allocation()
        child_1.evaluate_fitness()
        child_2.evaluate_fitness()
        self.step_solutions.extend([child_1, child_2])
        return [child_1, child_2]

    def __two_point_crossover(self, parent_1: Individual, parent_2: Individual) -> List[Individual]:
        chromosome_length = len(parent_1.chromosome)

        # Escolher dois pontos de corte diferentes
        cut_point_1 = random.randint(1, chromosome_length - 2)
        cut_point_2 = random.randint(cut_point_1 + 1, chromosome_length - 1)

        child_1_chromosome = (
                parent_1.chromosome[:cut_point_1] +
                parent_2.chromosome[cut_point_1:cut_point_2] +
                parent_1.chromosome[cut_point_2:]
        )

        child_2_chromosome = (
                parent_2.chromosome[:cut_point_1] +
                parent_1.chromosome[cut_point_1:cut_point_2] +
                parent_2.chromosome[cut_point_2:]
        )

        child_1 = Individual(parent_1.arbitrages, parent_1.budget)
        child_2 = Individual(parent_1.arbitrages, parent_1.budget)

        child_1.chromosome = child_1_chromosome
        child_2.chromosome = child_2_chromosome
        child_1.normalize_budget_allocation()
        child_2.normalize_budget_allocation()
        child_1.evaluate_fitness()
        child_2.evaluate_fitness()
        self.step_solutions.extend([child_1, child_2])
        return [child_1, child_2]

    def __normalize_fitness_population(self, solutions: List[Individual]):
        num_objectives = len(solutions[0].fitness)
        self.high_fitness_evaluated = [0 for _ in range(num_objectives)]

        for obj_index in range(num_objectives):
            for individual in solutions:
                if individual.fitness[obj_index] > self.high_fitness_evaluated[obj_index]:
                    self.high_fitness_evaluated[obj_index] = individual.fitness[obj_index]

        print(self.high_fitness_evaluated)
        for solution in solutions:
            solution.normalize_fitness(self.high_fitness_evaluated)

    def __initialize_pareto_fronts(self):
        """
            Inicializa as frentes de Pareto da população e identifica as soluções não dominadas na primeira frente.
       """
        # Inicialize as estruturas para armazenar as frentes de Pareto
        self.pareto_fronts = []
        for solution in self.solutions:
            solution.dominated_by = []
            solution.dominated_solutions = []
            solution.dominated_by_count = 0

        # Identifique as soluções não dominadas (frente de Pareto inicial)
        pareto_front = []
        for solution1 in self.solutions:
            is_dominated = False
            for solution2 in self.solutions:
                if solution1 is not solution2:
                    x1 = solution1.fitness_max_profit
                    y1 = solution1.fitness_diversification

                    x2 = solution2.fitness_max_profit
                    y2 = solution2.fitness_diversification

                    if ((x1 >= x2) and (y1 >= y2)) and ((x1 > x2) or (y1 > y2)):
                        solution1.dominated_solutions.append(solution2)

                    elif ((x2 >= x1) and (y2 >= y1)) and ((x2 > x1) or (y2 > y1)):
                        solution1.dominated_by.append(solution2)
                        solution1.dominated_by_count += 1
                        is_dominated = True

            if not is_dominated:
                solution1.rank = 1
                pareto_front.append(solution1)

        if len(pareto_front):
            self.pareto_history_front.append((self.generation, pareto_front))

        self.pareto_fronts.append(pareto_front)

    def __assign_rank(self):
        """
            Atribui um rank a cada solução com base em sua dominância em relação às outras soluções.
        """
        rank = 1
        current_front = self.pareto_fronts[0]

        while current_front:
            next_front = []

            for solution in current_front:
                solution.rank = rank
                for dominated_solution in solution.dominated_solutions:
                    dominated_solution.dominated_by_count -= 1
                    if dominated_solution.dominated_by_count == 0:
                        next_front.append(dominated_solution)

            rank += 1
            current_front = next_front
            if len(next_front) > 0:
                self.pareto_fronts.append(next_front)

    def __calculate_crowding_distance(self):
        for solution in self.solutions:
            solution.crowding_distance = 0

        num_objectives = len(self.solutions[0].fitness)

        for obj_index in range(num_objectives):
            sorted_solutions = sorted(self.solutions, key=lambda x: x.fitness[obj_index])
            sorted_solutions[0].crowding_distance = float('inf')
            sorted_solutions[-1].crowding_distance = float('inf')

            min_fitness = sorted_solutions[0].fitness[obj_index]
            max_fitness = sorted_solutions[-1].fitness[obj_index]

            for i in range(1, len(sorted_solutions) - 1):  # Excluindo o primeiro e último que já são infinitos
                sorted_solutions[i].crowding_distance += (
                        (sorted_solutions[i + 1].fitness[obj_index] - sorted_solutions[i - 1].fitness[obj_index])
                        / (max_fitness - min_fitness))

    def __select_survivors(self):
        survivors = []

        for front in self.pareto_fronts:
            front.sort(key=lambda x: (
                x.rank, -x.crowding_distance))  # Ordena por rank crescente e crowding distance decrescente
            survivors.extend(front)

            if len(survivors) >= self.n_individuals:
                break

        self.solutions = survivors[:self.n_individuals]  # Retorna os melhores indivíduos para a próxima geração

    def get_fitness_profit(self):
        return [individual.fitness_max_profit for individual in self.solutions]

    def get_fitness_diversification(self):
        return [individual.fitness_diversification for individual in self.solutions]

    def __commit_history_solutions(self):
        profits = [i.fitness[0] for i in self.solutions]
        dispersations = [i.fitness[1] for i in self.solutions]
        self.solutions_history.append((profits, dispersations))

    def __nsga_evaluation(self):
        self.__initialize_pareto_fronts()
        self.__assign_rank()
        self.__calculate_crowding_distance()

    def get_hypervolume(self):
        reference_point = [1.05, 1.05]
        x_values = [x for x, _ in self.pareto_history_front]
        y_values_reversed = [
            1 / pg.hypervolume([individual.fitness_normalized for individual in y]).compute(reference_point) for
            _, y in self.pareto_history_front]

        max_value = max(y_values_reversed)
        y_values_reversed = [i / max_value for i in y_values_reversed]
        return y_values_reversed[-1], sum(y_values_reversed)/len(y_values_reversed)

    def export_solutions(self):
        export = ExportadorDeGraficos()
        export.hypervolume_plot(self)
        export.generate_gif(self)

        x_data = []
        y_data = []
        for generation, front in self.pareto_history_front_normalized:
            x = [i[0] for i in front]
            y = [i[1] for i in front]
            if generation == 0 or generation == self.n_generations - 1:
                x_data.append(x)
                y_data.append(y)
                export.plot(x, y, generation)

    def __normalize_fitness(self):
        profit_list = []
        dispersation_list = []
        for generation, front in self.pareto_history_front:
            profit_list.extend([i.fitness[0] for i in front])
            dispersation_list.extend([i.fitness[1] for i in front])

        max_profit = max(profit_list)
        max_dispersation = max(dispersation_list)

        for generation, front in self.pareto_history_front:
            fitness_normalized = [(i.fitness[0] / max_profit, i.fitness[1] / max_dispersation) for i in front]
            self.pareto_history_front_normalized.append((generation, fitness_normalized))


# fo
if __name__ == '__main__':
    arbitrages = []
    arbitrages.append(
        Arbitrage("a86e2d9332c3ae6995a042ed4b95fe2b", 59664, 59631, "UNIBET_EU", "ONEXBET", 2.0, 2.02, 0.49))
    arbitrages.append(
        Arbitrage("a86e2d9332c3ae6995a042ed4b95fe2b", 59664, 59655, "UNIBET_EU", "PINNACLE", 2.0, 2.03, 0.73))
    arbitrages.append(
        Arbitrage("45c50eab0a379bd74d9ad5879ee50595", 94745, 94783, "ONEXBET", "UNIBET_EU", 1.9, 2.12, 0.19))
    arbitrages.append(
        Arbitrage("45c50eab0a379bd74d9ad5879ee50595", 94745, 94791, "ONEXBET", "MATCHBOOK", 1.9, 2.14, 0.63))
    arbitrages.append(
        Arbitrage("ff03cc32e860ac5cd4c907381443986f", 94795, 94833, "ONEXBET", "UNIBET_EU", 2.12, 1.91, 0.47))
    # arbitrages.append(Arbitrage("ff03cc32e860ac5cd4c907381443986f", 94840,	94833, "MATCHBOOK", "UNIBET_EU",	2.12,	1.91, 0.47))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 50050,	50043, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 50771,	50764, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 51606,	51599, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 56150,	56143, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 56932,	56925, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 59265,	59258, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))

    repository = SurebetRepository()

    start_date = '2023-09-01 19:55:00'
    end_date = '2023-09-01 20:00:00'
    arbitrages = repository.find_all_unique_between(start_date, end_date)

    export = ExportadorDeGraficos()
    simulations = []
    crossover = CrossOverEnum.UNIFORM_CROSSOVER_ONE_INDIVIDUAL
    # population = Population(arbitrages, 50, 100, crossover, 0.05, 200)
    for i in range(0, 9):
        print(f'{i + 1}º Simulation')
        population = Population(arbitrages, 50, 100, crossover, 0.01, 200)
        simulations.append(population)

    export.hypervolume_plots(simulations, crossover.name)

