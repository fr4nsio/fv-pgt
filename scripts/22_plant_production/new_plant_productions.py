#!/usr/bin/env python3

import httpx
import logging
import sys

PLANT_PRODUCTIONS: list[dict] = [
    # Mario Rossi.
    # 1
    {'daily_kwh': 5.78, 'monthly_kwh': 310.7, 'daily_power_range_id': 1, 'monthly_power_range_id': 1},

    # Giulio Bianchi.
    # 2
    {'daily_kwh': 3.71, 'monthly_kwh': 275.0, 'daily_power_range_id': 2, 'monthly_power_range_id': 2},

    # Impianto Sportivo "Ferrari".
    # 3
    {'daily_kwh': 7.3805, 'monthly_kwh': 641.9, 'daily_power_range_id': 3, 'monthly_power_range_id': 3},
]
URL: str = 'http://127.0.0.1:8080/plant_production'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for plant_production in PLANT_PRODUCTIONS:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=plant_production,
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
