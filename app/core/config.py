from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    DB_DRIVER: str = "sqlite"  # fallback
    SECRET_KEY: str

    @property
    def DB_URL(self) -> str:
        if self.DB_DRIVER.startswith("sqlite"):
            return f"sqlite:///{self.DB_NAME}.db"
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


settings = Settings()
# print(settings.DB_DRIVER)  # sanity check
# print(settings.DB_URL)
# print(settings.DB_HOST)
# print(settings.SECRET_KEY)
