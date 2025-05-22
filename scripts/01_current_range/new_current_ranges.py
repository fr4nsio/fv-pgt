#!/usr/bin/env python3

import httpx
import logging
import sys

CURRENT_RANGES: list[dict] = [
    ## PlantModuleSystem ##
    # Mario Rossi - DC.
    # 1
    {'lower': 10.1, 'upper': 20.0},

    # Giulio Bianchi - DC.
    # 2
    {'lower': 10.1, 'upper': 20.0},

    # Impianto Sportivo "Ferrari" - DC.
    # 3
    {'lower': 16.0, 'upper': 32.5},

    # Mario Rossi - AC.
    # 4
    {'lower': 13.0, 'upper': 17.0},

    # Giulio Bianchi - AC.
    # 5
    {'lower': 13.0, 'upper': 17.0},

    # Impianto Sportivo "Ferrari" - AC.
    # 6
    {'lower': 10.0, 'upper': 12.0},

    ## PlantBatterySystem ##
    # Mario Rossi - Master.
    # 7
    {'lower': 10.0, 'upper': 18.0},

    # Mario Rossi - Slave.
    # 8
    {'lower': 13.0, 'upper': 60.0},

    # Giulio Bianchi - Master.
    # 9
    {'lower': 10.0, 'upper': 18.0},

    # Giulio Bianchi - Slave.
    # 10
    {'lower': 13.0, 'upper': 60.0},

    # Impianto Sportivo "Ferrari" - Master.
    # 11
    {'lower': 0.1, 'upper': 18.0},

    # Impianto Sportivo "Ferrari" - Slave.
    # 12
    {'lower': 20.0, 'upper': 25.0},
]

URL: str = 'http://127.0.0.1:8080/current_range'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for current_range in CURRENT_RANGES:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=current_range,
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
