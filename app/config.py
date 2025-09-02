from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '..', '.env')

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
    "KAFKA_TOPIC": "asr",
    "DO_SEND_KAFKA_MESSAGES": True
}

class Settings(BaseSettings):

    load_dotenv(dotenv_path)

    ASR_SERVER: str = os.getenv("ASR_SERVER", default_config["ASR_SERVER"])
    ASR_PORT: str = os.environ.get("ASR_PORT", default_config["ASR_PORT"])
    ASR_MODEL: str = os.environ.get("ASR_MODEL", default_config["ASR_MODEL"])
    ASR_LANGUAGE: str = os.environ.get("ASR_LANGUAGE", default_config["ASR_LANGUAGE"])
    ASR_MUTE_AUDIO_PLAYBACK: bool = os.environ.get("ASR_MUTE_AUDIO_PLAYBACK", default_config["ASR_MUTE_AUDIO_PLAYBACK"])

    FASTAPI_SERVER: str = os.environ.get("FASTAPI_SERVER", default_config["FASTAPI_SERVER"])
    FASTAPI_PORT: str = os.environ.get("FASTAPI_PORT", default_config["FASTAPI_PORT"])

    #KAFKA_SERVER: str = "rebel.grivolla.net"
    KAFKA_SERVER: str = os.environ.get("KAFKA_SERVER", default_config["KAFKA_SERVER"])
    KAFKA_PORT: str = os.environ.get("KAFKA_PORT", default_config["KAFKA_PORT"])
    KAFKA_TOPIC: str = os.environ.get("KAFKA_TOPIC", default_config["KAFKA_TOPIC"])
    DO_PRINT_KAFKA_MESSAGES: bool = os.environ.get("DO_PRINT_KAFKA_MESSAGES", default_config.get("DO_PRINT_KAFKA_MESSAGES", False))
    DO_SEND_KAFKA_MESSAGES: bool = os.environ.get("DO_SEND_KAFKA_MESSAGES", default_config["DO_SEND_KAFKA_MESSAGES"])

settings = Settings()