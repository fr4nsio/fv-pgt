#!/usr/bin/env python3

import httpx
import logging
import sys

PLANTS: list[dict] = [
    {
        'name': 'Mario Rossi',
        'owner_id': 1,
        'plant_module_system_id': 1,
        'plant_battery_system_id': 1,
        'plant_production_id': 1,
        'installer': 'ENEL',
    },
    {
        'name': 'Giulio Bianchi',
        'owner_id': 2,
        'plant_module_system_id': 2,
        'plant_battery_system_id': 2,
        'plant_production_id': 2,
        'installer': 'EoN',
    },
    {
        'name': 'Impianto Sportivo "Ferrari"',
        'owner_id': 3,
        'plant_module_system_id': 3,
        'plant_battery_system_id': 3,
        'plant_production_id': 3,
        'installer': 'Ferrari',
    },
]
URL: str = 'http://127.0.0.1:8080/plant'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for plant in PLANTS:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=plant,
            headers={
                'Authorization': f'Bearer {TOKEN}',
            }
        )
        print(response.text)
        response.raise_for_status()
    except httpx.RequestError as exc:
        logging.error(f'An error occurred while requesting {exc.request.url!r}.')
        logging.error(exc)
        sys.exit(1)
