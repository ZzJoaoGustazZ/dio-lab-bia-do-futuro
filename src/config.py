"""Configurações e variáveis de ambiente do Vero."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Diretório base de dados (arquivos mockados do cliente)
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Credenciais e modelo do LLM (Google Gemini)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
MODEL_NAME = os.getenv("VERO_MODEL", "gemini-3.5-flash")

NOME_AGENTE = "Vero"
