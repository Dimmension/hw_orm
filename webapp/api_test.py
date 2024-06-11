"""Module for testing."""

import pytest
from . import application, utils_db, models

from sqlalchemy import create_engine
from http import HTTPStatus
from uuid import uuid4


@pytest.fixture(scope='module')
def test_app():
    """Test app.

    Yields:
        _type_: _description_
    """
    application.app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': utils_db.get_db_url_t(),
    })

    engine = create_engine(utils_db.get_db_url_t())

    models.Base.metadata.create_all(engine)

    yield application.app


@pytest.fixture(scope='module')
def client(test_app):
    """Test client.

    Args:
        test_app (_type_): _description_

    Returns:
        _type_: _description_
    """
    return test_app.test_client()


OK = 200


def test_empty_characters(client):
    """_summary_.

    Args:
        client (_type_): _description_
    """
    response = client.get('/characters')
    assert response.status_code == 200
    assert response.json == []


def test_create_character(client):
    """_summary_.

    Args:
        client (_type_): _description_
    """
    test_data = {
        'name': 'Test Character',
        'class_name': 'Warrior',
        'race_name': 'Elf',
        'damage': 10,
        'health': 100,
        'spell_id': str(uuid4()),
    }

    response = client.post('/characters/create', json=test_data)
    if response.status_code == HTTPStatus.BAD_REQUEST:
        assert response.json['error'] in ('incorrect uuid', f'spell with provided uuid({test_data["spell_id"]}) does not exits')
    else:
        assert response.status_code == HTTPStatus.CREATED
        assert 'id' in response.json


def test_get_characters(client):
    """_summary_.

    Args:
        client (_type_): _description_
    """
    response = client.get('/characters')
    assert response.status_code == HTTPStatus.OK
    assert isinstance(response.json, list)


def test_character_detail(client):
    """_summary_.

    Args:
        client (_type_): _description_
    """
    character_id = str(uuid4())
    response = client.get(f'/characters/{character_id}')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'error' in response.json


def test_update_character(client):
    """_summary_.

    Args:
        client (_type_): _description_
    """
    character_id = str(uuid4())
    test_data = {
        'name': 'Updated Character',
        'class_name': 'Mage',
        'race_name': 'Human',
        'damage': 15,
        'health': 90,
        'spell_id': str(uuid4()),
    }
    response = client.put(f'/characters/update/{character_id}', json=test_data)
    if response.status_code == HTTPStatus.BAD_REQUEST:
        assert response.json['error'] in ('incorrect uuid', f'spell with provided uuid({test_data["spell_id"]}) does not exits', f'character with provided uuid({character_id}) does not exits')
    else:
        assert response.status_code == HTTPStatus.OK
        assert 'result' in response.json


def test_delete_character(client):
    """_summary_.

    Args:
        client (_type_): _description_
    """
    character_id = str(uuid4())
    response = client.delete(f'/characters/delete/{character_id}')
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'error' in response.json


def test_fight(client):
    """_summary_.

    Args:
        client (_type_): _description_
    """
    fighter1 = str(uuid4())
    fighter2 = str(uuid4())
    test_data = {
        'fighter1': fighter1,
        'fighter2': fighter2,
    }
    response = client.post('/fight', json=test_data)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert 'error' in response.json
