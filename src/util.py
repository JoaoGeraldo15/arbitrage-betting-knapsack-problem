from src.config.config import PROJECT_PATH
import os


def checkout_root_path():
    # Altera o diretório de trabalho atual para o diretório raiz do código
    os.chdir(PROJECT_PATH)
