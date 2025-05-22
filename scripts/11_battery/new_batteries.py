#!/usr/bin/env python3

import httpx
import logging
import sys

BATTERIES: list[dict] = [
    # Mario Rossi - Master.
    # 1
    {'name': 'Modulo BMS (Master)', 'battery_specification_id': 1},

    # Mario Rossi - Slave.
    # 2
    {'name': 'Battery slave', 'battery_specification_id': 2},

    # Giulio Bianchi - Master.
    # 3
    {'name': 'Modulo BMS (Master)', 'battery_specification_id': 3},

    # Giulio Bianchi - Slave.
    # 4
    {'name': 'Battery slave', 'battery_specification_id': 4},

    # Impianto Sportivo "Ferrari" - Master.
    # 5
    {'name': 'Modulo BMS (Master)', 'battery_specification_id': 5},

    # Impianto Sportivo "Ferrari" - Slave.
    # 6
    {'name': 'Battery slave', 'battery_specification_id': 6},
]
URL: str = 'http://127.0.0.1:8080/battery'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for battery in BATTERIES:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=battery,
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
