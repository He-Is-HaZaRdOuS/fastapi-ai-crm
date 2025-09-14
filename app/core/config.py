from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DRIVER: str = "sqlite"  # fallback
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"
    PORT: int = 8000

    @property
    def DB_URL(self) -> str:
        if self.DB_DRIVER.startswith("sqlite"):
            return f"sqlite:///{self.DB_NAME}.db"
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
