import math
import pickle
import random
from enum import Enum
from typing import List

import matplotlib
from numpy.distutils.fcompiler import pg


class CrossOverEnum(Enum):
    UNIFORM_CROSSOVER = 1
    UNIFORM_CROSSOVER_ONE_INDIVIDUAL = 2
    ONE_POINT_CROSSOVER = 3


class Plot:
    def __init__(self):
        pass

    @staticmethod
    def hv_plot(self, population):
        reference_point = [1.1, 1.1]

        x_values = [x for x, _ in population.pareto_history_front]
        y_values = [pg.hypervolume([individual.fitness_normalized for individual in y]).compute(reference_point) for
                    _, y in population.pareto_history_front]

        # Invertendo a solução para melhorar a visualização já que é um problema de maximização
        y_values_reversed = [
            1 / pg.hypervolume([individual.fitness_normalized for individual in y]).compute(reference_point) for _, y in
            population.pareto_history_front]
        max_value = max(y_values_reversed)

        y_values_reversed = [i / max_value for i in y_values_reversed]
        self.generate_hv_plot(x_values, y_values, max(y_values) + 0.05)
        self.generate_hv_plot(x_values, y_values_reversed, max(y_values_reversed) + 0.05)

    def generate_hv_plot(self, x, y, y_axis_limit):
        hv = matplotlib.pyplot
        hv.xlabel('Generation')
        hv.ylabel('Hypervolume')
        hv.xlim(-1, max(x)+2)
        hv.ylim(0, y_axis_limit)
        hv.plot(x, y)
        hv.grid(True)
        hv.show()


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
        self.normalize_budge_allocation()
        self.evaluate_fitness()

    def normalize_budge_allocation(self):
        total = sum([chromosome[1] for chromosome in self.chromosome if chromosome[0] == 1])

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

    def objective_function_min_withdraw(self):
        # função que será pensada no futuro
        pass

    def objective_function_diversification(self):
        entropy = 0
        for index in range(len(self.chromosome)):
            gene = self.chromosome[index]
            if gene[0] == 1:
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
    def __init__(self, arbitrages, budget, crossover_strategy: CrossOverEnum, generations=10):
        """
        Inicializa a população de soluções no contexto do algoritmo NSGA-II.

        Args:
            num_individuals (int): O número de indivíduos na população.
            arbitrages (list): É uma lista de objetos Arbitrage representando as oportunidades de arbitragem.
            budget (float): Orçamento disponível para alocação nas apostas.
        """

        self.crossover_strategy = crossover_strategy
        self.num_individuals = len(arbitrages)
        self.solutions: List[Individual] = []  # Lista de todas as soluções
        self.step_solutions: List[Individual] = []  # Lista auxiliar que será usada para construir a geração de filhos
        self.high_fitness_evaluated = [0, 0]
        self.pareto_fronts = []  # Lista de listas representando as frentes de Pareto
        self.solutions_history: List = []
        self.pareto_history_front = []
        self.generations = generations
        self.generation = 0

        for _ in range(self.num_individuals):
            individual = Individual(arbitrages, budget, init_population=True)
            self.solutions.append(individual)

        self.__main()

    def __main(self):
        self.__normalize_fitness_population(self.solutions)
        self.__nsga_evaluation()
        self.__commit_history_solutions()

        # Selecionar os pais e realizar cruzamento, mutação até ter uma população 2N
        while self.generation < self.generations:
            self.step_solutions = []
            while len(self.step_solutions) < self.num_individuals:  # Gerando os filhos
                self.__evolve(self.crossover_strategy, self.__tournament_selection(), self.__tournament_selection())
            self.__normalize_fitness_population(self.step_solutions)
            self.solutions.extend(self.step_solutions[: self.num_individuals])
            self.__nsga_evaluation()
            self.__select_survivors()
            self.__commit_history_solutions()
            self.generation += 1


    def __evolve(self, enum: CrossOverEnum, parent_1: Individual, parent_2: Individual):
        childes: List[Individual] = []
        if enum.value == CrossOverEnum.UNIFORM_CROSSOVER:
            childes = self.__uniform_crossover(parent_1, parent_2)
        elif enum.value == CrossOverEnum.UNIFORM_CROSSOVER_ONE_INDIVIDUAL:
            childes = [self.__uniform_crossover_one_individual(parent_1, parent_2)]
        else:
            childes = self.__one_point_crossover(parent_1, parent_2)

        for child in childes:
            if random.random() < 0.05:
                self.__mutation(child)

    def __tournament_selection(self) -> Individual:
        tournament = random.sample(self.solutions, 2)
        tournament.sort(key=lambda x: (x.rank, -x.crowding_distance))
        return tournament[0]

    def __mutation(self, child: Individual):
        print('Mutou')
        print(f'Antes: {child.chromosome} --> {child.fitness}')
        random_index = random.randrange(len(child.chromosome))
        if child.chromosome[random_index][0] == 1:
            child.chromosome[random_index] = (0, child.chromosome[random_index][1])
        else:
            child.chromosome[random_index] = (1, child.chromosome[random_index][1])

        child.normalize_budge_allocation()
        child.evaluate_fitness()
        print(f'Depois: {child.chromosome} --> {child.fitness}')

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

        child_1.normalize_budge_allocation()
        child_2.normalize_budge_allocation()
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

        child.normalize_budge_allocation()
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
        child_1.normalize_budge_allocation()
        child_2.normalize_budge_allocation()
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

            if len(survivors) >= self.num_individuals:
                break

        self.solutions = survivors[:self.num_individuals]  # Retorna os melhores indivíduos para a próxima geração

    def get_fitness_profit(self):
        return [individual.fitness_max_profit for individual in self.solutions]

    def get_fitness_diversification(self):
        return [individual.fitness_diversification for individual in self.solutions]

    def __commit_history_solutions(self):
        profits = [i.fitness_normalized[0] for i in self.solutions]
        dispersations = [i.fitness_normalized[1] for i in self.solutions]
        self.solutions_history.append((profits, dispersations))

    def __nsga_evaluation(self):
        self.__initialize_pareto_fronts()
        self.__assign_rank()
        self.__calculate_crowding_distance()


# class Solution:
#     def __init__(self, fitness_max_profit, fitness_diversification, fitness):
#         """
#             Inicializa uma solução individual no contexto do algoritmo NSGA-II.
#
#         Args:
#             fitness_max_profit (float): O valor de fitness para a maximização do lucro máximo.
#             fitness_diversification (float): O valor de fitness para a diversificação.
#             fitness
#         """
#         self.fitness_max_profit = fitness_max_profit
#         self.fitness_diversification = fitness_diversification
#         self.fitness = fitness # lista com todas os fitness
#         self.fitness_normalized = 0 # lista com todas os fitness
#         self.dominated_by = []  # Lista de soluções que dominam esta solução
#         self.dominated_solutions = []  # Lista de soluções que esta solução domina
#         self.dominated_by_count = 0  # Por quantas soluções esta solução é dominada
#         self.rank = None  # Rank da solução nas frentes de Pareto
#         self.crowding_distance = None  # Distância de lotação da solução


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
    # TODO Para o NSGA-II tem que normalizar para ficar com escala 0 a 1, para todas as funções objetivo.

    # individuo = Individual(arbitrages, 100)
    population = Population(arbitrages, 100)

