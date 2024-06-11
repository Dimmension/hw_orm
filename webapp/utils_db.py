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
    url = 'postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'
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
    url = 'postgresql+psycopg://{POSTGRES_USER_T}:{POSTGRES_PASSWORD_T}@{POSTGRES_HOST_T}:{POSTGRES_PORT_T}/{POSTGRES_DB_T}'
    return url.format(**credentials)
