# =============================================================================
# mi_m_t/config.py — application configuration (pydantic-settings)
# tags:    [μS-CAND][TRIG-REQ]
# date:    2026-04-29
# citation: ARCH-SPEC §7.1 (stack assumptions)
# =============================================================================
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Database
    db_driver: str = "sqlite"          # sqlite | mysql | postgres
    db_host: str = "127.0.0.1"
    db_port: int = 3306
    db_name: str = "mi_m_t_dev"
    db_user: str = ""
    db_pass: str = ""

    # SQLite LDE path (used when db_driver == sqlite)
    sqlite_path: str = ".test/d06.sqlite"

    # Application
    app_env: str = "development"       # development | production
    debug: bool = True
    base_url: str = ""
    secret_key: str = "change-me-in-production"

    # Pagination defaults
    default_page_size: int = 50
    max_page_size: int = 200

    @property
    def database_url(self) -> str:
        if self.db_driver == "sqlite":
            return f"sqlite+aiosqlite:///{self.sqlite_path}"
        if self.db_driver == "mysql":
            return (
                f"mysql+asyncmy://{self.db_user}:{self.db_pass}"
                f"@{self.db_host}:{self.db_port}/{self.db_name}"
            )
        # postgres
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_pass}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()
