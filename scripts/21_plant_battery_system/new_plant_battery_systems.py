#!/usr/bin/env python3

import httpx
import logging
import sys
import random


makes: list[str] = ['Tesla', 'ENEL', 'Agip', 'EoN', 'Q8', 'Repsol', 'Xiaomi']

PLANT_BATTERY_SYSTEMS: list[dict] = [
    # Mario Rossi.
    # 1
    {'battery_ids': [1, 2], 'make': random.choice(makes)},

    # Giulio Bianchi.
    # 2
    {'battery_ids': [3, 4], 'make': random.choice(makes)},

    # Impianto Sportivo "Ferrari".
    # 3
    {'battery_ids': [5, 6], 'make': random.choice(makes)},
]
URL: str = 'http://127.0.0.1:8080/plant_battery_system'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for plant_battery_system in PLANT_BATTERY_SYSTEMS:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=plant_battery_system,
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
