from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    ASR_SERVER: str = "renfe-whisperlive-gpu-asr"
    ASR_PORT: str = "9090"
    ASR_MODEL: str = "tiny"
    ASR_LANGUAGE: str = "es"
    ASR_MUTE_AUDIO_PLAYBACK: bool = True

    FASTAPI_SERVER: str = "localhost"
    FASTAPI_PORT: str = "8050"

    KAFKA_SERVER: str = "rebel.grivolla.net"
    KAFKA_PORT: str = "9092"

settings = Settings()