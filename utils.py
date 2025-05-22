from flask import jsonify
from typing import Any
from sqlalchemy import select, and_, or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
import mashumaro
import logging
import time


def validate_json(obj_schema, request_data) -> tuple[bool, Any]:
    r"""Funzione di convenienza per validare lo schema JSON in input dalle richieste HTTP."""
    try:
        return True, obj_schema.from_json(request_data)
    except (mashumaro.exceptions.MissingField,
            mashumaro.exceptions.ExtraKeysError,
            mashumaro.exceptions.UnserializableField,
            mashumaro.exceptions.InvalidFieldValue,
            ValueError) as e:
         return False, (jsonify({'error': str(e)}), 400,)
    except Exception as e:
         return False, (jsonify({'error': 'unknown error: ' + str(e)}), 400,)


def new_db_object(obj: Any, db: Any, max_retries: int = 10000, delay: float = 0.1, return_raw: bool = False) -> tuple:
    r"""Funzione di convenienza per salvare oggetti nel database e ritonare una risposta."""
    attempt: int = 0

    while attempt < max_retries:
        try:
            db.session.add(obj)
            db.session.commit()
            logging.info(f'Object added: {obj.serialize()}')
            db.session.flush()
            if return_raw:
                return obj.serialize()
            else:
                return jsonify({'data': obj.serialize()}), 201
        except IntegrityError as e:
            db.session.rollback()
            logging.error(f'IntegrityError on attempt {attempt + 1}: {str(e)}')
            attempt += 1
            time.sleep(delay)
        except SQLAlchemyError as e:
            db.session.rollback()
            logging.error(f'SQLAlchemyError on attempt {attempt + 1}: {str(e)}')
            attempt += 1
            time.sleep(delay)
        except Exception as e:
            db.session.rollback()
            logging.error(f'Unexpected error: {str(e)}')
            return jsonify({'error': 'Unexpected error: ' + str(e)}), 500

    return jsonify({'error': 'Failed to add object after multiple attempts.'}), 500


def list_db_objects(obj_class: Any, db: Any) -> Any:
    try:
        objs = db.session.query(obj_class).all()
        return jsonify([obj.serialize() for obj in objs])
    except Exception as e:
        return jsonify({"error": "could not retrieve objects"}), 500



def detail_raw_db_object(obj_class: Any, obj_id: int, db: Any) -> Any:
    r"""Semplice filtro tabella database per id."""
    try:
        return db.session.execute(
            select(obj_class).where(obj_class.id == obj_id)
        ).scalars().first()
    except Exception as e:
        return jsonify({"error": "Could not retrieve object"}), 500


def detail_db_object(obj_class: Any, obj_id: int, db: Any, respond_api: bool = True, obj_name: str = '') -> Any:
    r"""Funzione di convenienza per vedere i dettagli di un oggetto."""
    obj = detail_raw_db_object(obj_class, obj_id, db)

    if obj_name == '':
        obj_name = 'object'

    if obj is None:
        if respond_api:
            return jsonify({'error': f'{obj_name} {obj_id} not found'}), 404
        else:
            return obj
    else:
        if respond_api:
            return jsonify(obj.serialize()), 200
        else:
            return obj


if __name__ == '__main__':
    pass

