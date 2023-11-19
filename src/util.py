import math
import os
import datetime
import pickle
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


class PickleSerializer:
    @staticmethod
    def save(obj, filename):
        """Salva o objeto em um arquivo usando pickle."""
        with open(filename, 'wb') as file:
            pickle.dump(obj, file)

    @staticmethod
    def load(filename):
        """Carrega um objeto de um arquivo usando pickle."""
        with open(filename, 'rb') as file:
            return pickle.load(file)


class ExportadorDeGraficos:

    def __init__(self):
        self.data_hora_atual = f'{datetime.datetime.now().strftime("%Y_%m_%d_[%H:%M:%S]")}_{str(uuid.uuid4())[:5]}'
        os.mkdir(self.data_hora_atual)

    def get_file_name(self, geracoes, extension=''):
        return f'{self.data_hora_atual}_[G:{geracoes}].{extension}'

    def plot(self, x, y, generation):
        plt = matplotlib.pyplot
        plt.figure()
        # plt.xlim(0, 1.05)
        # plt.ylim(0, 1.05)
        plt.title(f'{generation}° Geração')
        plt.xlabel('Lucro')
        plt.ylabel('Distribuição de surebets')
        plt.scatter(x, y)
        plt.savefig(self.data_hora_atual + '/' + self.get_file_name(generation, 'png'))
        plt.close()

    def generate_gif(self, population):
        plt = matplotlib.pyplot
        metadata = dict(title='NSGA-II', artist='João Geraldo')
        writer = PillowWriter(fps=5, metadata=metadata)
        file_name = self.data_hora_atual + '/' + self.get_file_name(population.n_generations, 'gif')

        fig, ax = plt.subplots()
        ax.set_xlim(0, 1.05)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel('Lucro')
        ax.set_ylabel('Distribuição de surebets')

        with writer.saving(fig, file_name, 100):
            for i, solutions in enumerate(population.solutions_history):
                ax.clear()
                ax.set_title(f'Gerações: {i}/{population.n_generations} População: {population.n_individuals}')
                ax.scatter(solutions[0], solutions[1], color='#FF5500', s=5)
                writer.grab_frame()

        plt.close()

    def __plot_hv(self, x, y, y_axis_limit, title, filename):

        plt = matplotlib.pyplot
        plt.xlabel('Gerações')
        plt.ylabel('Valor do Hypervolume')
        plt.title(title)
        plt.xlim(-1, max(x) + 2)
        plt.ylim(0, y_axis_limit)
        plt.xticks([i for i in range(0, len(x)+1, 15)])
        plt.scatter(x, y, s=15)
        plt.savefig(self.data_hora_atual + '/' + filename)
        plt.close()

    def hypervolume_plot(self, population):
        x_values, y_values = self.calculate_hypervolume(population)

        title = f'Tamanho da população: {population.n_individuals} Taxa de Mutação: {population.mutation_rate}'
        self.__plot_hv(x_values, y_values, max(y_values) * 1.1, title, 'hypervolume.png')

    def calculate_hypervolume(self, population):
        reference_point = [0.05, 0.05]
        x_values = []
        y_values = []
        pareto_evolution = []
        for g, front in population.pareto_history_front_negative:
            x_values.append(g)
            hypervolume = pg.hypervolume(front).compute(reference_point)
            y_values.append(hypervolume)

            if len(pareto_evolution) == 0 or hypervolume > pareto_evolution[-1][0]:
                pareto_evolution.append((hypervolume, [[-i[0], -i[1]] for i in front]))

        population.evolution_front = pareto_evolution

        population.best_frontier = y_values.index(max(y_values))
        return x_values, y_values

    def __config_sub_plot_hv(self) -> matplotlib.pyplot:
        plot_config = matplotlib.pyplot
        plot_config.figure(figsize=(16, 12))
        plot_config.xlabel('Gerações')
        plot_config.ylabel('Hypervolume')
        return plot_config

    def hypervolume_plots(self, population_list: [], main_title: str):
        n_columns = 4
        n_rows = int(np.ceil(len(population_list) / n_columns))

        plt.figure(figsize=(n_columns * 4, n_rows * 4))
        count = 1

        for population in population_list:
            x_values, y_values = self.calculate_hypervolume(population)

            title = f'[P]: {population.n_individuals} [G]: {population.n_generations} [M]: {population.mutation_rate} [C]: {population.crossover_rate}'

            plt.subplot(n_rows, n_columns, count)
            plt.scatter(x_values, y_values)
            plt.title(title)
            count += 1

        plt.suptitle(main_title, fontsize=16)  # Título principal
        # plt.tight_layout() # Ajuste o layout dos subgráficos
        plt.subplots_adjust(wspace=0.2, hspace=0.5)
        plt.savefig(f'{self.data_hora_atual}_{main_title}_.pdf')
        plt.close()

        # imagem = Image.open(f'{self.data_hora_atual}.png')
        # imagem.show()

    def grid_hypervolume(self, population_list: [], params):
        reference_point = [1.0, 1.0]

        # n_rows = int(np.ceil(np.sqrt(len(population_list))))
        # n_columns = int(np.ceil(len(population_list) / n_rows))
        n_columns = 3
        n_rows = int(np.ceil(len(population_list) / n_columns))

        # plot_config: matplotlib.pyplot = self.__config_sub_plot_hv()
        plt.figure(figsize=(n_columns * 4, n_rows * 4))

        count = 1
        for population in population_list:
            x_values, y_values = self.calculate_hypervolume(population)

            title = f'[P]: {population.n_individuals} [G]: {population.n_generations} [M]: {population.mutation_rate} \n{population.crossover_strategy.name}'

            plt.subplot(n_rows, n_columns, count)
            plt.plot(x_values, y_values)
            plt.title(title)

            if population.n_individuals == params[0] and population.n_generations == params[
                1] and population.mutation_rate == params[2] and population.crossover_strategy == params[3]:
                plt.title(title, color='green')

            count += 1

        # plt.tight_layout() # Ajuste o layout dos subgráficos
        plt.subplots_adjust(wspace=0.2, hspace=0.5)
        plt.savefig(f'{self.data_hora_atual}.pdf')
        plt.close()

        # imagem = Image.open(f'{self.data_hora_atual}.pdf')
        # imagem.show()

    def get_max_hypervolume(self, population):
        _, y_values = self.calculate_hypervolume(population)
        return max(y_values)
