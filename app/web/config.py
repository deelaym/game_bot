import os
from dataclasses import dataclass

import yaml
from dotenv import load_dotenv

load_dotenv()


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "project"


@dataclass
class BotConfig:
    token: str


@dataclass
class Config:
    echo: bool = True
    bot: BotConfig | None = None
    database: DatabaseConfig | None = None


def setup_config(app, config_path):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    raw_config_env = {
        "database": {
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB"),
        },
        "bot": {"token": os.getenv("BOT_TOKEN")},
    }

    if raw_config_env["bot"]["token"]:
        raw_config.update(raw_config_env)

    app.config = Config(
        bot=BotConfig(
            token=raw_config["bot"]["token"],
        ),
        database=DatabaseConfig(**raw_config["database"]),
        echo=raw_config["debug"]["echo"],
    )
