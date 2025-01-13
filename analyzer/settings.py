import os

from dotenv import load_dotenv

load_dotenv()

USE_CSV = os.getenv('USE_CSV') == 'True'

POSTGRES_URL = os.getenv('POSTGRES_URL')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
