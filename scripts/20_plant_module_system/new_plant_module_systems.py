#!/usr/bin/env python3

import httpx
import logging
import sys
import random


makes: list[str] = ['Tesla', 'ENEL', 'Agip', 'EoN', 'Q8', 'Repsol', 'Xiaomi']

PLANT_MODULE_SYSTEMS: list[dict] = [
    # Mario Rossi.
    # 1
    {'ac_current_id': 1, 'dc_current_id': 1, 'capacity': 6.0, 'make': random.choice(makes)},

    # Giulio Bianchi.
    # 2
    {'ac_current_id': 2, 'dc_current_id': 2, 'capacity': 6.0, 'make': random.choice(makes)},

    # Impianto Sportivo "Ferrari".
    # 3
    {'ac_current_id': 3, 'dc_current_id': 3, 'capacity': 10.0, 'make': random.choice(makes)},
]

URL: str = 'http://127.0.0.1:8080/plant_module_system'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for plant_module_system in PLANT_MODULE_SYSTEMS:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=plant_module_system,
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
