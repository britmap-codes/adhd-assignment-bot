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


import os
from pathlib import Path

ENV_PATH = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'infra', '.env') 
)
 

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr



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

print(settings)

# sanity check
print("Using .env:", ENV_PATH)
print("Exists?    ", os.path.exists(ENV_PATH))