import math
import os
import datetime
import uuid
from enum import Enum

import matplotlib
import numpy as np
# from PIL.Image import Image
from matplotlib import pyplot as plt
from matplotlib.animation import PillowWriter
import pygmo as pg

from src.config.config import API_KEY
# from src.genetic.arbitrage import Population
from PIL import Image


def checkout_root_path():
    # Altera o diretório de trabalho atual para o diretório raiz do código
    os.chdir('/home/joaogeraldo/TCC/fetch-api')


def replace_api_key(api_key):
    file_path = '/home/joaogeraldo/TCC/fetch-api/.env'
    keys = API_KEY.split(',')
    new_api_key = ','.join([key for key in keys if key not in api_key])

    with open(file_path, 'r') as file:
        lines = file.readlines()

    with open(file_path, 'w') as file:
        for line in lines:
            if line.startswith("API_KEY="):
                line = f"API_KEY={new_api_key}\n"
            file.write(line)


class BookmakerWithdrawEnum(Enum):
    # Saques mínimo via PIX
    BETSSON = 50
    MATCHBOOK = 10  # https://www.matchbook.com/page/faqs/accountfunding
    PINNACLE = 30  #  https://www.pinnacle.com/pt/future/legal-payments
    WILLIAMHILL = 10  #  https://williamhill-lang.custhelp.com/app/answers/detail/a_id/28879
    SPORT_888 = 50  #  https://www.888sport.com/pt/banking/withdrawal/policy/#CashOutPolicy
    ONEXBET = 30  #  https://br.1xbet.com/information/payment
    UNIBET_EU = 10
    BETONLINEAG = 50
    NORDICBET = 20


class ExportadorDeGraficos:

    def __init__(self):
        self.data_hora_atual = f'{datetime.datetime.now().strftime("%Y_%m_%d_[%H:%M:%S]")}_{str(uuid.uuid4())[:5]}'
        print(self.data_hora_atual)
        os.mkdir(self.data_hora_atual)

    def get_file_name(self, geracoes, extension=''):
        return f'{self.data_hora_atual}_[G:{geracoes}].{extension}'


    def plot(self, x, y, generation):
        plt = matplotlib.pyplot
        plt.figure()
        plt.xlim(0, 1.05)
        plt.ylim(0, 1.05)
        plt.title(f'{generation}° Generation')
        plt.xlabel('Profit')
        plt.ylabel('Dispersation')
        plt.scatter(x, y)
        plt.grid(True)
        plt.savefig(self.data_hora_atual + '/' + self.get_file_name(generation, 'png'))
        plt.close()

    def generate_gif(self, population):
        plt = matplotlib.pyplot
        metadata = dict(title='NSGA-II', artist='João Geraldo')
        writer = PillowWriter(fps=5, metadata=metadata)
        fig = plt.figure()
        l, = plt.plot([], [], 'ko', markersize=5)
        plt.setp(l, color='#FF5500')
        plt.xlim(0, 1.05)
        plt.ylim(0, 1.05)
        plt.xlabel('Profit')
        plt.ylabel('Dispersation')
        file_name = self.data_hora_atual+ '/' + self.get_file_name(population.n_generations, 'gif')

        with writer.saving(fig, file_name, 100):
            for i in range(len(population.solutions_history)):
                # plt.title(f'{i}° Generation')
                plt.title(f'Generation: {i}/{population.n_generations} Population: {population.n_individuals}')
                l.set_data(population.solutions_history[i][0], [population.solutions_history[i][1]])
                writer.grab_frame()

        plt.close()

    def __plot_hv(self, x, y, y_axis_limit, title, filename):
        plt = matplotlib.pyplot
        plt.xlabel('Generation')
        plt.ylabel('Hypervolume')
        plt.title(title)
        plt.xlim(-1, max(x) + 2)
        plt.ylim(0, y_axis_limit)
        plt.plot(x, y)
        plt.grid(True)
        plt.savefig(self.data_hora_atual + '/' + filename)
        plt.close()

    def hypervolume_plot(self, population):
        reference_point = [1.1, 1.1]
        x_values = [x for x, _ in population.pareto_history_front_normalized]
        y_values = [pg.hypervolume([i for i in y]).compute(reference_point) for _, y in population.pareto_history_front_normalized]

        y_values_reversed = [1 / pg.hypervolume([i for i in y]).compute(reference_point) for _, y in population.pareto_history_front_normalized]
        max_value = max(y_values_reversed)
        y_values_reversed = [i / max_value for i in y_values_reversed]
        title = f'[P]: {population.n_individuals} [G]: {population.n_generations} [M]: {population.mutation_rate} [C]: {population.crossover_strategy}'
        self.__plot_hv(x_values, y_values_reversed, max(y_values_reversed) + max(y_values_reversed) * 0.1, title, 'hypervolume.png')

        y_values_reversed = [math.log10(i + 1) for i in y_values_reversed]
        self.__plot_hv(x_values, y_values_reversed, max(y_values_reversed) + max(y_values_reversed) * 0.1, title + ' log10', 'hypervolume_log.png')

    def __config_sub_plot_hv(self) -> matplotlib.pyplot:
        plot_config = matplotlib.pyplot
        plot_config.figure(figsize=(16, 12))
        plot_config.xlabel('Generation')
        plot_config.ylabel('Hypervolume')
        return plot_config

    def hypervolume_plots(self, population_list: [], main_title: str):
        reference_point = [1.1, 1.1]
        x_values = [x for x, _ in population_list[0].pareto_history_front_normalized]

        n_columns = 3
        n_rows = int(np.ceil(len(population_list) / n_columns))

        plt.figure(figsize=(n_columns * 4, n_rows * 4))
        count = 1

        for population in population_list:
            y_values_reversed = [
                1 / pg.hypervolume([i for i in y]).compute(reference_point) for
                _, y in population.pareto_history_front_normalized]

            max_value = max(y_values_reversed)
            y_values_reversed = [i / max_value for i in y_values_reversed]
            # y_values_reversed = [math.log10(i + 1) for i in y_values_reversed]
            # title = f'Population: {population.n_individuals} Generations: {population.n_generations} Mutation: {population.mutation_rate}'
            title = f'[P]: {population.n_individuals} [G]: {population.n_generations} [M]: {population.mutation_rate}'

            plt.subplot(n_rows, n_columns, count)
            plt.plot(x_values, y_values_reversed)
            plt.title(title)
            count += 1

        plt.suptitle(main_title, fontsize=16)  # Título principal
        # plt.tight_layout() # Ajuste o layout dos subgráficos
        plt.subplots_adjust(wspace=0.2, hspace=0.5)
        plt.savefig(f'{self.data_hora_atual}.png')
        plt.close()

        imagem = Image.open(f'{self.data_hora_atual}.png')
        imagem.show()

    def grid_hypervolume(self, population_list: [], params):
        reference_point = [1.1, 1.1]

        # n_rows = int(np.ceil(np.sqrt(len(population_list))))
        # n_columns = int(np.ceil(len(population_list) / n_rows))
        n_columns = 3
        n_rows = int(np.ceil(len(population_list) / n_columns))

        # plot_config: matplotlib.pyplot = self.__config_sub_plot_hv()
        plt.figure(figsize=(n_columns * 4, n_rows * 4))

        count = 1
        for population in population_list:
            x_values = [x for x, _ in population.pareto_history_front_normalized]
            y_values_reversed = [
                1 / pg.hypervolume([i for i in y]).compute(reference_point) for
                _, y in population.pareto_history_front_normalized]

            max_value = max(y_values_reversed)
            y_values_reversed = [i / max_value for i in y_values_reversed]

            title = f'[P]: {population.n_individuals} [G]: {population.n_generations} [M]: {population.mutation_rate} \n{population.crossover_strategy.name}'

            # if population.n_individuals == params[0] and population.n_generations == params[1] and population.mutation_rate == params[2] and population.crossover_strategy == params[3]:
            #     print(ax.spines)
            #     ax.set_title(title, color='green')

            plt.subplot(n_rows, n_columns, count)
            plt.plot(x_values, y_values_reversed)
            plt.title(title)

            if population.n_individuals == params[0] and population.n_generations == params[1] and population.mutation_rate == params[2] and population.crossover_strategy == params[3]:
                plt.title(title, color='green')

            count += 1

        # plt.tight_layout() # Ajuste o layout dos subgráficos
        plt.subplots_adjust(wspace=0.2, hspace=0.5)
        plt.savefig(f'{self.data_hora_atual}.pdf')
        plt.close()

        # imagem = Image.open(f'{self.data_hora_atual}.pdf')
        # imagem.show()
