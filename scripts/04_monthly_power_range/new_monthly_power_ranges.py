#!/usr/bin/env python3

import httpx
import logging
import sys

MONTHLY_POWER_RANGES: list[dict] = [
    # Mario Rossi.
    # 1
    {'lower': 350.0, 'upper': 899.0},

    # Giulio Bianchi.
    # 2
    {'lower': 350.0, 'upper': 899.0},

    # Impianto Sportivo "Ferrari".
    # 3
    {'lower': 350.0, 'upper': 1699.9},
]

URL: str = 'http://127.0.0.1:8080/monthly_power_range'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for monthly_power_range in MONTHLY_POWER_RANGES:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=monthly_power_range,
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
