#!/usr/bin/env python3

import httpx
import logging
import sys

VOLTAGE_RANGES: list[dict] = [
    ## PlantModuleSystem ##
    # Mario Rossi - DC.
    # 1
    {'lower': 47.0, 'upper': 319.0},

    # Giulio Bianchi - DC.
    # 2
    {'lower': 47.0, 'upper': 319.0},

    # Impianto Sportivo "Ferrari" - DC.
    # 3
    {'lower': 300.0, 'upper': 600.0},

    # Mario Rossi - AC.
    # 4
    {'lower': 230.0, 'upper': 245.0},

    # Giulio Bianchi - AC.
    # 5
    {'lower': 230.0, 'upper': 245.0},

    # Impianto Sportivo "Ferrari" - AC.
    # 6
    {'lower': 200.0, 'upper': 400.0},

    ## PlantBatterySystem ##
    # Mario Rossi - Master.
    # 7
    {'lower': 49.0, 'upper': 50.0},

    # Mario Rossi - Slave.
    # 8
    {'lower': 49.0, 'upper': 50.0},

    # Giulio Bianchi - Master.
    # 9
    {'lower': 49.0, 'upper': 50.0},

    # Giulio Bianchi - Slave.
    # 10
    {'lower': 49.0, 'upper': 50.0},

    # Impianto Sportivo "Ferrari" - Master.
    # 11
    {'lower': 160.0, 'upper': 600.0},

    # Impianto Sportivo "Ferrari" - Slave.
    # 12
    {'lower': 160.0, 'upper': 600.0},
]
URL: str = 'http://127.0.0.1:8080/voltage_range'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for voltage_range in VOLTAGE_RANGES:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=voltage_range,
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
