# import os
# interacts with Operation System since it is saved locally
# from dotenv import load_dotenv, find_dotenv
#   Find .env automatically by walking up directories until its found
# dotenv_path = find_dotenv()
#   Load entries as environment variables
# load_dotenv(dotenv_path)
# telegram_bot_token = os.getenv("BOT_TOKEN")
# telegram_webhook_url = os.getenv("WEBHOOK_URL")
#   other_variable = os.getenv("OTHER_VARIABLE")
#database_url = os.getenv("SUPABASE_DATABASE_URL")


#----------------------------------------------------------
# Switched to pydantic settings to include type, validation, and defaults to prevent errors

from __future__ import annotations
from typing import Iterable
import os
from pathlib import Path

# ENV_PATH = os.path.realpath(
#     os.path.join(os.path.dirname(__file__), '..', '..', 'infra', '.env') 
# )
 

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr




def get_project_root(start: Path,
    root_indicators: Iterable[str] = (".git", "pyproject.toml", "requirements.txt"),):
    ''' Walks upwards from path (start) until it finds the project root folder containing .git,
      pyproject.toml, requirements.txt, "docker-compose.yml", etc.
    '''
    current_path = start.resolve()
    indicators = set(root_indicators)
    while True:

        print(f"Current directory: {current_path}")
        if any((current_path / indicator).exists() for indicator in indicators):
            return current_path
        if current_path == current_path.parent:
            raise RuntimeError("Project root not found. No root indicators present.")
        current_path = current_path.parent

# 1) Project root (no hard-coded C:\ paths)
ROOT_DIR: Path = get_project_root(Path(__file__).resolve().parent)

# 2) Storage root (configurable)
# Allow override via env var, else default to <repo>/storage
STORAGE_DIR: Path = Path(os.getenv("STORAGE_DIR", str(ROOT_DIR / "storage"))).expanduser().resolve()

# 3) Standard subfolders
ORIGINALS_DIR: Path = STORAGE_DIR / "originals"
CLEANED_DIR: Path = STORAGE_DIR / "cleaned"
CHUNKS_DIR: Path = STORAGE_DIR / "chunks"
EXPORTS_DIR: Path = STORAGE_DIR / "exports"
LOGS_DIR: Path = ROOT_DIR / "logs"

# Create folders automatically (fresh clone safe)
for p in (STORAGE_DIR, ORIGINALS_DIR, CLEANED_DIR, CHUNKS_DIR, EXPORTS_DIR, LOGS_DIR):
    p.mkdir(parents=True, exist_ok=True)

# .env path derived from project root (robust)
ENV_PATH: Path = (ROOT_DIR / "infra" / ".env").resolve()



class Settings(BaseSettings):
    TELEGRAM_BOT_TOKEN: SecretStr
    TELEGRAM_WEBHOOK_URL: SecretStr
    FQDN: SecretStr #n8n url
    GENERIC_TIMEZONE: str = "America/Toronto"
    GROQ_API_KEY: SecretStr # used secret str instead str to hide secrets from being shown
    SUPABASE_API_KEY: SecretStr | None = None #not immediately using db yet
    SUPABASE_DATABASE_URL: SecretStr | None = None

    model_config = SettingsConfigDict(
    #encountered issues previously because .env is in different folder from config.py, pydantic couldn't find .env file
        env_file = ENV_PATH,  
        env_file_encoding="utf-8",
    )
    
    
    

settings = Settings()

# print(settings)

# sanity check
# print("Using .env:", ENV_PATH)
# print("Exists?    ", os.path.exists(ENV_PATH))

# Sanity Check
# Optional sanity checks (safe-ish). Enable by setting DEBUG_CONFIG=1
if os.getenv("DEBUG_CONFIG", "0") == "1":
    print("ROOT_DIR:    ", ROOT_DIR)
    print("STORAGE_DIR: ", STORAGE_DIR)
    print("ENV_PATH:    ", ENV_PATH)
    print("ENV exists?: ", ENV_PATH.exists())
