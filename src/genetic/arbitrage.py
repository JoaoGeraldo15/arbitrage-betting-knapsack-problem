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
        self.fitness = 0
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
        print(f"{self.chromosome} --> {[sum([chromosome[1] for chromosome in self.chromosome if chromosome[0] == 1])]}")
        self.normalize()
        print(f"{self.chromosome} --> {[sum([chromosome[1] for chromosome in self.chromosome if chromosome[0] == 1])]}")

    def normalize(self):
        total = sum([chromosome[1] for chromosome in self.chromosome if chromosome[0] == 1])

        for index in range(len(self.chromosome)):
            chromosome = self.chromosome[index]
            if chromosome[0] == 1:
                new_value_normalized = round(chromosome[1]/total, 2)
                self.chromosome[index] = (1, new_value_normalized)
    def check_fitness(self):
        for index in range(len(self.chromosome)):
            gene = self.chromosome[index]
            if gene[0] == 1:
                # print(f'self.profits[index]: {self.profits[index]} * (gene[1]: {gene[1]} * self.budget: {self.budget}) = {round(self.profits[index] * (gene[1] * self.budget), 2)} ')
                self.fitness += round(self.profits[index] * (gene[1] * self.budget), 2)
        print(f'Fitness: {self.fitness}')

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

    individuo = Individual(arbitrages, 100)
    individuo.check_fitness()
    # for i in individuo.chromosome:
    #     print(i, end=' ')
    # print()

