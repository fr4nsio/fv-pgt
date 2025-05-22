#!/usr/bin/env python3

import httpx
import logging
import sys

FREQUENCY_RANGES: list[dict] = [
        # Mario Rossi - AC.
        # 1
        {'lower': 45.0, 'upper': 51.0},

        # Giulio Bianchi - AC.
        # 2
        {'lower': 45.0, 'upper': 51.0},

        # Impianto Sportivo "Ferrari" - AC.
        # 3
        {'lower': 45.0, 'upper': 66.0},
]
URL: str = 'http://127.0.0.1:8080/frequency_range'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for frequency_range in FREQUENCY_RANGES:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=frequency_range,
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
