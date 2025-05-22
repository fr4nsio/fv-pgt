#!/usr/bin/env python3

import httpx
import logging
import sys

DC_CURRENT_SYSTEMS: list[dict] = [
    # Mario Rossi.
    {'voltage_range_id': 1, 'current_range_id': 1},

    # Giulio Bianchi.
    {'voltage_range_id': 2, 'current_range_id': 2},

    # Impianto Sportivo "Ferrari".
    {'voltage_range_id': 3, 'current_range_id': 3},
]
URL: str = 'http://127.0.0.1:8080/dc_current_system'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for dc_current_system in DC_CURRENT_SYSTEMS:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=dc_current_system,
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
