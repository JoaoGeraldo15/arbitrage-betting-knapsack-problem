import os
from dotenv import load_dotenv

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

load_dotenv()

API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")
HOST = 'https://api.the-odds-api.com'