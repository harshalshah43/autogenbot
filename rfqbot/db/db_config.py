import os
# from dotenv import load_dotenv

# load_dotenv("../..")


class ConfigDB:
    REQUIRED_ENV_VARS = ["DB_USER", "DB_PASSWORD", "DB_HOST", "DB_NAME"]

    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
    if missing:
        raise EnvironmentError(
            f"Missing required db environment variables: {', '.join(missing)}"
        )
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_NAME = os.getenv("DB_NAME")

    @classmethod
    def db_url(cls):
        return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}/{cls.DB_NAME}?sslmode=require"