import os
from dotenv import load_dotenv

load_dotenv()


GOOGLE_API_KEY_1 = os.getenv("GOOGLE_API_KEY_1")
if not GOOGLE_API_KEY_1:
    raise ValueError("A chave GOOGLE_API_KEY_1 não foi encontrada no arquivo .env")

GOOGLE_API_KEY_2 = os.getenv("GOOGLE_API_KEY_2")
if not GOOGLE_API_KEY_2:
    raise ValueError("A chave GOOGLE_API_KEY_2 não foi encontrada no arquivo .env")