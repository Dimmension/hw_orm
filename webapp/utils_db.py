"""Module that provides config for application."""

import os

import dotenv


def get_db_url_test() -> str:
    """Provide URL to database.

    Returns:
        str: url to database.
    """
    dotenv.load_dotenv()
    postgres_vars = {
        'POSTGRES_HOST',
        'POSTGRES_PORT',
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'POSTGRES_DB',
    }
    credentials = {db_var: os.environ.get(db_var) for db_var in postgres_vars}
    url = 'postgresql+psycopg://user1:password1@127.0.0.1:5435/database1'
    return url.format(**credentials)


def get_db_url_t() -> str:
    """Provide URL to database.

    Returns:
        str: url to database.
    """
    dotenv.load_dotenv()
    postgres_vars = {
        'POSTGRES_HOST_T',
        'POSTGRES_PORT_T',
        'POSTGRES_USER_T',
        'POSTGRES_PASSWORD_T',
        'POSTGRES_DB_T',
    }
    credentials = {db_var: os.environ.get(db_var) for db_var in postgres_vars}
    url = 'postgresql+psycopg://user2:password2@127.0.0.1:5433/database2'
    return url.format(**credentials)
