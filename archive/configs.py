import argparse
import os

from loguru import logger


class Config:
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--env",
            choices=["staging", "testing", "development", "production"],
            default="development",
        )
        args = parser.parse_args()

        self.environment = args.env
        self.settings = self.load_settings()

    def load_settings(self):
        if self.environment == "staging":
            return self.load_staging_settings()
        elif self.environment == "testing":
            return self.load_testing_settings()
        elif self.environment == "development":
            return self.load_development_settings()
        elif self.environment == "production":
            return self.load_production_settings()

    def load_staging_settings(self):
        logger.debug("STAGING")
        return {
            "db": "staging_db",
            "user": os.getenv("STAGING_USER"),
            "password": os.getenv("STAGING_PASSWORD"),
            # Add more settings as needed
        }

    def load_testing_settings(self):
        logger.debug("TESTING")
        return {
            "db": os.getenv("TESTING_DB"),
            "user": os.getenv("TESTING_USER"),
            "password": os.getenv("TESTING_PASSWORD"),
            # Add more settings as needed
        }

    def load_development_settings(self):
        logger.debug("DEVELOPMENT")
        return {
            "db": os.getenv("DEVELOPMENT_DB"),
            "user": os.getenv("DEVELOPMENT_USER"),
            "password": os.getenv("DEVELOPMENT_PASSWORD"),
            # Add more settings as needed
        }

    def load_production_settings(self):
        logger.debug("PRODUCTION")
        return {
            "db": os.getenv("PRODUCTION_DB"),
            "user": os.getenv("PRODUCTION_USER"),
            "password": os.getenv("PRODUCTION_PASSWORD"),
            # Add more settings as needed
        }


config = Config()
