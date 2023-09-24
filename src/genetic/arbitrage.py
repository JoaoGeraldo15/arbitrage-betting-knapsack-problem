import math
from random import random


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
    def __init__(self, arbitrages, budget, geracao=0):
        self.arbitrages = arbitrages
        self.profits = [i.profit for i in arbitrages]
        self.budget = budget
        self.geracao = geracao
        self.fitness = []
        self.fitness_max_profit = None
        self.fitness_diversification = None
        self.chromosome = []

        total_profit = 0
        count_profit = 0

        for i in range(len(arbitrages)):
            valor = round(random(), 2)
            if valor < 0.5:
                self.chromosome.append((0, valor))
            else:
                self.chromosome.append((1, valor))
                total_profit += self.profits[i]
                count_profit += 1

        self.normalize()
        self.evaluate_fitness()

    def normalize(self):
        total = sum([chromosome[1] for chromosome in self.chromosome if chromosome[0] == 1])

        for index in range(len(self.chromosome)):
            chromosome = self.chromosome[index]
            if chromosome[0] == 1:
                new_value_normalized = round(chromosome[1]/total, 2)
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
        self.objective_function_max_profit()
        self.objective_function_diversification()


class Population:
    def __init__(self, num_individuals, arbitrages, budget):
        """
        Inicializa a população de soluções no contexto do algoritmo NSGA-II.

        Args:
            num_individuals (int): O número de indivíduos na população.
            arbitrages (list): É uma lista de objetos Arbitrage representando as oportunidades de arbitragem.
            budget (float): Orçamento disponível para alocação nas apostas.
        """
        self.num_individuals = num_individuals
        self.solutions = []  # Lista de todas as soluções
        self.pareto_fronts = []  # Lista de listas representando as frentes de Pareto

        for _ in range(num_individuals):
            individual = Individual(arbitrages, budget)
            self.solutions.append(Solution(individual.fitness_max_profit, individual.fitness_diversification, [individual.fitness_max_profit, individual.fitness_diversification]))

        self.initialize_pareto_fronts()
        self.assign_rank()
        self.calculate_crowding_distance()

    def initialize_pareto_fronts(self):
        """
            Inicializa as frentes de Pareto da população e identifica as soluções não dominadas na primeira frente.

       """
        # Inicialize as estruturas para armazenar as frentes de Pareto
        for solution in self.solutions:
            solution.dominated_by = []
            solution.dominated_by_count = 0

        # Identifique as soluções não dominadas (frente de Pareto inicial)
        pareto_front = []
        for solution1 in self.solutions:
            is_dominated = False
            for solution2 in self.solutions:
                if solution1 is not solution2:
                    if (solution1.fitness_max_profit >= solution2.fitness_max_profit
                            and solution1.fitness_diversification >= solution2.fitness_diversification):
                        solution1.dominated_solutions.append(solution2)

                    elif (solution2.fitness_max_profit >= solution1.fitness_max_profit
                            and solution2.fitness_diversification >= solution1.fitness_diversification):
                        solution1.dominated_by.append(solution2)
                        solution1.dominated_by_count += 1
                        is_dominated = True

            if not is_dominated:
                solution1.rank = 1
                pareto_front.append(solution1)

        self.pareto_fronts.append(pareto_front)

    def assign_rank(self):
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

    def calculate_crowding_distance(self):
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
                sorted_solutions[i].crowding_distance += ((sorted_solutions[i + 1].fitness[obj_index] - sorted_solutions[i - 1].fitness[obj_index])
                                                          / (max_fitness - min_fitness))

    def select_survivors(self, num_individuals):
        survivors = []

        for front in self.pareto_fronts:
            front.sort(key=lambda x: (-x.rank, x.crowding_distance))  # Ordene por rank decrescente e distância de lotação crescente
            survivors.extend(front)

            if len(survivors) >= num_individuals:
                break

        return survivors[:num_individuals]  # Retorna os melhores indivíduos para a próxima geração

    def get_fitness_profit(self):
        return [individual.fitness_max_profit for individual in self.solutions]

    def get_fitness_diversification(self):
        return [individual.fitness_diversification for individual in self.solutions]


class Solution:
    def __init__(self, fitness_max_profit, fitness_diversification, fitness):
        """
            Inicializa uma solução individual no contexto do algoritmo NSGA-II.

        Args:
            fitness_max_profit (float): O valor de fitness para a maximização do lucro máximo.
            fitness_diversification (float): O valor de fitness para a diversificação.
            fitness
        """
        self.fitness_max_profit = fitness_max_profit
        self.fitness_diversification = fitness_diversification
        self.fitness = fitness # lista com todas os fitness
        self.dominated_by = []  # Lista de soluções que dominam esta solução
        self.dominated_solutions = []  # Lista de soluções que esta solução domina
        self.dominated_by_count = 0  # Por quantas soluções esta solução é dominada
        self.rank = None  # Rank da solução nas frentes de Pareto
        self.crowding_distance = None  # Distância de lotação da solução


# fo
if __name__ == '__main__':
    arbitrages = []
    arbitrages.append(Arbitrage("a86e2d9332c3ae6995a042ed4b95fe2b", 59664,	59631, "UNIBET_EU", "ONEXBET",	2.0,	2.02, 0.49))
    arbitrages.append(Arbitrage("a86e2d9332c3ae6995a042ed4b95fe2b", 59664,	59655, "UNIBET_EU", "PINNACLE",	2.0,	2.03, 0.73))
    arbitrages.append(Arbitrage("45c50eab0a379bd74d9ad5879ee50595", 94745,	94783, "ONEXBET", "UNIBET_EU",	1.9,	2.12, 0.19))
    arbitrages.append(Arbitrage("45c50eab0a379bd74d9ad5879ee50595", 94745,	94791, "ONEXBET", "MATCHBOOK",	1.9,	2.14, 0.63))
    arbitrages.append(Arbitrage("ff03cc32e860ac5cd4c907381443986f", 94795,	94833, "ONEXBET", "UNIBET_EU",	2.12,	1.91, 0.47))
    # arbitrages.append(Arbitrage("ff03cc32e860ac5cd4c907381443986f", 94840,	94833, "MATCHBOOK", "UNIBET_EU",	2.12,	1.91, 0.47))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 50050,	50043, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 50771,	50764, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 51606,	51599, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 56150,	56143, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 56932,	56925, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))
    # arbitrages.append(Arbitrage("6454621f739da2ded2aaae7694e8835a", 59265,	59258, "ONEXBET", "NORDICBET",	2.08,	1.95, 0.64))
    # TODO Para o NSGA-II tem que normalizar para ficar com escala 0 a 1, para todas as funções objetivo.

    # individuo = Individual(arbitrages, 100)
    population = Population(5, arbitrages, 100)
    print(population.pareto_fronts)












