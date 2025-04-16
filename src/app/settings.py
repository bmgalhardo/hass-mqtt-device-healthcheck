import logging

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    broker_uri: str = "192.168.1.237"
    timeout: int = 5
    logging: str = "INFO"

    def set_log_level(self):
        logging.basicConfig(level=self.logging, force=True)

settings = Settings()
settings.set_log_level()
