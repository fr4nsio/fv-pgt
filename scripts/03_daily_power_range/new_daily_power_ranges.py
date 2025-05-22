#!/usr/bin/env python3

import httpx
import logging
import sys

DAILY_POWER_RANGES: list[dict] = [
    # Mario Rossi.
    # 1
    {'lower': 0.1, 'upper': 5.999},

    # Giulio Bianchi.
    # 2
    {'lower': 0.1, 'upper': 5.999},

    # Impianto Sportivo "Ferrari".
    # 3
    {'lower': 0.1, 'upper': 9.999},
]
URL: str = 'http://127.0.0.1:8080/daily_power_range'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for daily_power_range in DAILY_POWER_RANGES:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=daily_power_range,
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
