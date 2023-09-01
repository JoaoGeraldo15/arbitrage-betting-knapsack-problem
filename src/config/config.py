import os
from dotenv import load_dotenv

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

load_dotenv()

API_KEY = os.getenv("API_KEY")
LAST_API_KEY_USED = os.getenv("LAST_API_KEY_USED")
DATABASE_URL = os.getenv("DATABASE_URL")
PROJECT_PATH = os.getenv("PROJECT_PATH")
SRC_PATH = os.getenv("SRC_PATH")
SCRIPTS_PATH = os.getenv("SCRIPTS_PATH")
REPOSITORY_PATH = os.getenv("REPOSITORY_PATH")
SERVICE_PATH = os.getenv("SERVICE_PATH")
HOST = 'https://api.the-odds-api.com'
