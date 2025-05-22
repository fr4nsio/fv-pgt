#!/usr/bin/env python3

import httpx
import logging
import sys
import pprint

URLS: list[str] = [
    'http://127.0.0.1:8080/plant_module_system_sensor_reading',
    'http://127.0.0.1:8080/plant_module_system_sensor_reading?plant_id=1',
    'http://127.0.0.1:8080/plant_module_system_sensor_reading?plant_id=2',
    'http://127.0.0.1:8080/plant_module_system_sensor_reading?plant_id=1&results=2',
    'http://127.0.0.1:8080/plant_module_system_sensor_reading?plant_id=2&results=2',
]
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)

for url in URLS:
    response: str = ''
    try:
        response = httpx.get(
            url,
            headers={
                'Authorization': f'Bearer {TOKEN}',
            }
        )
        response.raise_for_status()
        pprint.pprint(response.json())
    except httpx.RequestError as exc:
        logging.error(f'An error occurred while requesting {exc.request.url!r}.')
        logging.error(exc)
        sys.exit(1)
