from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    database_url: str
    jwt_secret:str
    jwt_algorithm:str
    # redis_host:str = "localhost"
    # redis_port:int = 6379

    redis_url: str = "redis://localhost:6379/0"

    MAIL_USERNAME:str
    MAIL_PASSWORD:str
    MAIL_FROM:str
    MAIL_PORT:int
    MAIL_SERVER:str
    MAIL_FROM_NAME:str
    MAIL_TLS:bool = True
    MAIL_SSL:bool = False
    USE_CREDENTIALS:bool = True
    VALIDATE_CERTS:bool = True

    DOMAIN:str


    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


Config = AppConfig()

broker_url = Config.redis_url
result_backend = Config.redis_url