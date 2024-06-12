"""Main application module."""
import os
from http import HTTPStatus
from uuid import UUID

from flask import Flask, request
from psycopg.errors import UniqueViolation
from sqlalchemy import create_engine, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from . import models
from . import utils_db

DEFAULT_FLASK_PORT = 5001
ERROR = 'error'


def create_app() -> Flask:
    """Create app instance.

    Returns:
        Flask: app instance
    """
    app = Flask(__name__)
    app.json.ensure_ascii = False
    return app


app = create_app()
app.json.ensure_ascii = False
engine = create_engine(utils_db.get_db_url_t(), echo=True)
models.Base.metadata.create_all(engine)


def validator_uuid4(uuid_to_test: str) -> bool:
    """Validate correctness of uuid.

    Args:
        uuid_to_test (str): input uuid

    Returns:
        bool: True if string is uuid4
    """
    try:
        uuid_obj = UUID(uuid_to_test, version=4)
    except ValueError:
        return False
    return str(uuid_obj) == uuid_to_test


def validator_spell_id(body: dict) -> str:
    """Validate correctness of spell_id.

    Args:
        body (dict): request data.

    Returns:
        str: type of error or ok.
    """
    if body.get('spell_id'):
        if not validator_uuid4(body['spell_id']):
            return 'incorrect uuid'
        with Session(engine) as session:
            request_spell_id = select(models.Spell).where(models.Spell.id == body['spell_id'])
            if not session.scalar(request_spell_id):
                return 'does not exists'
    return 'ok'


@app.get('/')
def hello_world() -> tuple[str, HTTPStatus]:
    """Endpoint basic.

    Returns:
        tuple[dict, HTTPStatus]: response json and HTTP code
    """
    return '<p>Hello, World!</p>', HTTPStatus.OK


@app.get('/characters')
def get_characters() -> tuple[list, HTTPStatus]:
    """Endpoint for get all characters.

    Returns:
        tuple[dict, HTTPStatus]: response json and HTTP code
    """
    with Session(engine) as session:
        characters = session.scalars(select(models.Character)).all()
        characters = [character.as_dict() for character in characters]
        session.commit()
        session.commit()
    return characters, HTTPStatus.OK


@app.get('/characters/<character_id>')
def character_detail(character_id: str) -> tuple[dict, HTTPStatus]:
    """Endpoint for get character details.

    Args:
        character_id (str): uuid of character.

    Returns:
        tuple[dict, HTTPStatus]: response json and HTTP code
    """
    with Session(engine) as session:
        request_character = select(models.Character).where(models.Character.id == character_id)
        character = session.scalar(request_character)
        if not character:
            return {
                ERROR: f'character with provided uuid({character_id}) does not exits',
            }, HTTPStatus.BAD_REQUEST
        res = character.as_dict()
        session.commit()
    return res, HTTPStatus.OK


@app.post('/characters/create')
def create_characters() -> tuple[dict, HTTPStatus]:
    """Endpoint for create character.

    Returns:
        tuple[dict, HTTPStatus]: response json and HTTP code
    """
    body = request.json
    if not body['name'] or not body['class_name'] or not body['race_name'] or not body['damage'] or not body['health']:
        return {ERROR: 'Name, class_name and race_name and damage and heatlh are required'}, HTTPStatus.BAD_REQUEST

    if validator_spell_id(body) == 'incorrect uuid':
        return {ERROR: 'incorrect uuid'}, HTTPStatus.BAD_REQUEST
    elif validator_spell_id(body) == 'does not exists':
        return {
            ERROR: f'spell with provided uuid({body["spell_id"]}) does not exits',
        }, HTTPStatus.BAD_REQUEST

    with Session(engine) as session:
        character = models.Character(**body)
        try:
            session.add(character)
            session.commit()
        except (IntegrityError, UniqueViolation):
            session.rollback()
            return {'error': 'character already exists'}, HTTPStatus.CONFLICT
        character_id = character.id
        session.commit()

    return {'id': character_id}, HTTPStatus.CREATED


@app.put('/characters/update/<character_id>')
def update_character(character_id: str) -> tuple[dict, HTTPStatus]:
    """Endpoint for update character by uuid.

    Args:
        character_id (str): uuid of character.

    Returns:
        tuple[dict, HTTPStatus]: response json and HTTP code
    """
    body = request.json

    if validator_spell_id(body) == 'incorrect uuid':
        return {ERROR: 'incorrect uuid'}, HTTPStatus.BAD_REQUEST
    elif validator_spell_id(body) == 'does not exists':
        return {
            ERROR: f'spell with provided uuid({body["spell_id"]}) does not exits',
        }, HTTPStatus.BAD_REQUEST

    with Session(engine) as session:
        request_character = select(models.Character).where(models.Character.id == character_id)
        character = session.scalar(request_character)
        if not character:
            return {
                ERROR: f'character with provided uuid({character_id}) does not exits',
            }, HTTPStatus.BAD_REQUEST
        request_update = update(models.Character).where(models.Character.id == character_id)
        session.execute(request_update.values(**body))
        session.commit()
    return {'result': f'successfully update characted with uuid({character_id})'}, HTTPStatus.OK


@app.delete('/characters/delete/<character_id>')
def delete_character(character_id: str) -> tuple[dict, HTTPStatus]:
    """Endpoint for delete character.

    Args:
        character_id (str): uuid of character.

    Returns:
        tuple[dict, HTTPStatus]: response json and HTTP code
    """
    with Session(engine) as session:
        request_character = select(models.Character).where(models.Character.id == character_id)
        character = session.scalar(request_character)
        if not character:
            return {
                ERROR: f'character with provided uuid({character_id}) does not exits',
            }, HTTPStatus.BAD_REQUEST
        session.delete(character)
        session.commit()
    return {'result': f'successfully deleted characted with uuid({character_id})'}, HTTPStatus.OK


@app.post('/fight')
def fight() -> tuple[dict, HTTPStatus]:
    """Do fight between fighters.

    Returns:
        tuple[dict, HTTPStatus]: _description_
    """
    body = request.json
    fighter1 = body['fighter1']
    fighter2 = body['fighter2']

    with Session(engine) as session:
        request_character1 = select(models.Character).where(models.Character.id == fighter1)
        character1 = session.scalar(request_character1)

        request_character2 = select(models.Character).where(models.Character.id == fighter2)
        character2 = session.scalar(request_character2)

        if not character1 or not character2:
            return {
                ERROR: 'characters not exits',
            }, HTTPStatus.BAD_REQUEST

        figh1 = character1
        figh2 = character2

        if figh1.health > 0 and figh2.health > 0:
            figh2.health -= figh1.damage
            if figh2.health <= 0:
                return {'result': f'{figh1} won!)'}, HTTPStatus.OK

            figh1.health -= figh2.damage
            if figh1.health <= 0:
                return {'result': f'{figh1} won!'}, HTTPStatus.OK

            return {'result': 'draw!'}, HTTPStatus.OK
        session.commit()

    return {'result': 'Error during fight!'}, HTTPStatus.OK


if __name__ == '__main__':
    try:
        port = int(os.getenv('FLASK_PORT', DEFAULT_FLASK_PORT))
    except ValueError:
        port = DEFAULT_FLASK_PORT
    app.run(port=DEFAULT_FLASK_PORT, debug=False)
