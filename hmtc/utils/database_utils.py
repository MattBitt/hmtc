import psycopg2
from loguru import logger
from hmtc.config import init_config

config = init_config()


def delete_and_create_database():

    env = config["general"]["environment"]
    if env == "production":
        logger.error("Cannot delete database in production")
        return
    db_config = {
        "host": config["database"]["host"],
        "database": config["database"]["name"],
        "user": config["database"]["user"],
        "password": config["database"]["password"],
        "port": config["database"]["port"],
    }
    conn = psycopg2.connect(**db_config)
    conn.autocommit = True
    cursor = conn.cursor()
    db_name = config["database"]["name"]
    db_user = config["database"]["user"]

    delete_database(cursor, db_name)
    create_database(cursor, db_name, db_user)
    cursor.close()
    conn.close()


def delete_database(cursor, db_name):

    drop_cmd = f"DROP DATABASE IF EXISTS {db_name};"

    cursor.execute(drop_cmd)


def create_database(cursor, db_name, db_user):
    create_cmd = f"CREATE DATABASE '{db_name}' WITH OWNER {db_user};"
    grant_cmd = f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}"
    cursor.execute(create_cmd)
    cursor.execute(grant_cmd)
