from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://secop_user:secop_pass_dev@localhost:5432/secop_monitor"

    # OpenAI
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Resend
    resend_api_key: str = ""
    alert_email_to: str = "equipo@dtgrowthpartners.com"
    alert_email_from: str = "secop@dtgrowthpartners.com"

    # App
    relevance_threshold: int = 60
    alert_threshold: int = 70
    sync_interval_hours: int = 6
    backfill_days: int = 90

    # SECOP APIs
    secop_ii_url: str = "https://www.datos.gov.co/resource/p6dx-8zbt.json"
    secop_i_url: str = "https://www.datos.gov.co/resource/jbjy-vk9h.json"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
