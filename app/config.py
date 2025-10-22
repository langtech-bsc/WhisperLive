from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path_default = os.path.abspath(join(dirname(__file__), '..', '.env'))
dotenv_path = os.path.abspath(os.getenv("DOTENV_PATH", dotenv_path_default))

default_config = {
    "ASR_SERVER": "renfe-whisperlive-gpu-asr",
    "ASR_PORT": "9090",
    "ASR_MODEL": "tiny",
    "ASR_LANGUAGE": "es",
    "ASR_MUTE_AUDIO_PLAYBACK":  True,
    "FASTAPI_SERVER": "localhost",
    "FASTAPI_PORT": "8050",
    "KAFKA_SERVER": "hetzner.grivolla.net",
    "KAFKA_PORT": "19094",
    "KAFKA_TOPIC": "call_transcript",
    "DO_PRINT_KAFKA_MESSAGES": False,
    "DO_SEND_KAFKA_MESSAGES": True,    
    "DO_ALWAYS_SEND_ASR_KAFKA_MESSAGES": False
}

def getenv(var_name, default_value):
    """function to get environment variable or default value and print which one is used"""

    if var_name in os.environ:
        # if os.environ[var_name].lower() in ['true', 'false']:
        #     os.environ[var_name] = bool(os.environ[var_name])
        print(f"Using environment variable for {var_name}: {os.environ[var_name]}")
        return os.environ[var_name]
    else:
        # if default_value not in [True, False]:
        #     default_value = "None"
        print(f"Using default value for {var_name}: {default_value}")   
        return default_value

class Settings(BaseSettings):

    if os.path.exists(dotenv_path):
        print(f"Loading .env file from {dotenv_path}")
        load_dotenv(dotenv_path)
    else:
        print(f".env file not found at {dotenv_path}, using environment variables or default values.")

    # if not os.path.exists(dotenv_path):
    #     print(f".env file not found at {dotenv_path}, using environment variables or default values.")

    ASR_SERVER: str = getenv("ASR_SERVER", default_config["ASR_SERVER"])
    ASR_PORT: str = getenv("ASR_PORT", default_config["ASR_PORT"])
    ASR_MODEL: str = getenv("ASR_MODEL", default_config["ASR_MODEL"])
    ASR_LANGUAGE: str = getenv("ASR_LANGUAGE", default_config["ASR_LANGUAGE"])
    ASR_MUTE_AUDIO_PLAYBACK: bool = getenv("ASR_MUTE_AUDIO_PLAYBACK", default_config["ASR_MUTE_AUDIO_PLAYBACK"])

    FASTAPI_SERVER: str = getenv("FASTAPI_SERVER", default_config["FASTAPI_SERVER"])
    FASTAPI_PORT: str = getenv("FASTAPI_PORT", default_config["FASTAPI_PORT"])

    #KAFKA_SERVER: str = "rebel.grivolla.net"
    KAFKA_SERVER: str = getenv("KAFKA_SERVER", default_config["KAFKA_SERVER"])
    KAFKA_PORT: str = getenv("KAFKA_PORT", default_config["KAFKA_PORT"])
    KAFKA_TOPIC: str = getenv("KAFKA_TOPIC", default_config["KAFKA_TOPIC"])
    DO_PRINT_KAFKA_MESSAGES: bool = getenv("DO_PRINT_KAFKA_MESSAGES", default_config["DO_PRINT_KAFKA_MESSAGES"])
    DO_SEND_KAFKA_MESSAGES: bool = getenv("DO_SEND_KAFKA_MESSAGES", default_config["DO_SEND_KAFKA_MESSAGES"])
    DO_ALWAYS_SEND_ASR_KAFKA_MESSAGES: bool = getenv("DO_ALWAYS_SEND_ASR_KAFKA_MESSAGES", default_config["DO_ALWAYS_SEND_ASR_KAFKA_MESSAGES"])

settings = Settings()