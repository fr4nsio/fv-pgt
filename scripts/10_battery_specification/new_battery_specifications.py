#!/usr/bin/env python3

import httpx
import logging
import sys

BATTERY_SPECIFICATIONS: list[dict] = [
    # Mario Rossi - Master.
    # 1
    {'type': 'master', 'voltage_range_id': 7, 'current_range_id': 7, 'capacity': 10.0},

    # Mario Rossi - Slave.
    # 2
    {'type': 'slave', 'voltage_range_id': 8, 'current_range_id': 8, 'capacity': 10.0},

    # Giulio Bianchi - Master.
    # 3
    {'type': 'master', 'voltage_range_id': 9, 'current_range_id': 9, 'capacity': 9.7},

    # Giulio Bianchi - Slave.
    # 4
    {'type': 'slave', 'voltage_range_id': 10, 'current_range_id': 10, 'capacity': 9.7},

    # Impianto Sportivo "Ferrari" - Master.
    # 5
    {'type': 'master', 'voltage_range_id': 11, 'current_range_id': 11, 'capacity': 30.0},

    # Impianto Sportivo "Ferrari" - Slave.
    # 6
    {'type': 'slave', 'voltage_range_id': 12, 'current_range_id': 12, 'capacity': 30.0},
]
URL: str = 'http://127.0.0.1:8080/battery_specification'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for battery_specification in BATTERY_SPECIFICATIONS:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=battery_specification,
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
