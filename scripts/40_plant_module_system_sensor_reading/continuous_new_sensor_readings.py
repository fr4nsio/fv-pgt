#!/usr/bin/env python3

import random
import httpx
import logging
import sys
import time
import datetime
from new_plant_module_system_sensor_readings import gen_data


URL: str = 'http://127.0.0.1:8080/plant_module_system_sensor_reading'
TOKEN: str = 'hello-0-a'

logging.basicConfig(level=logging.INFO)

while True:
    # Ho bisogno di letture attuali.
    data = gen_data(readings_per_plant_module_system=1, hours_diff=0)

    error_counter: int = 0
    for d in data:
        response: str = ''
        try:
            response = httpx.post(
                URL,
                json=d,
                headers={
                    'Authorization': f'Bearer {TOKEN}',
                }
            )
            response.raise_for_status()
        except httpx.RequestError as exc:
            logging.error(f'An error occurred while requesting {exc.request.url!r}.')
            logging.error(exc)
            error_counter += 1

        if error_counter >= 4:
            logging.error('too many errors: quitting')
            sys.exit(1)

        time.sleep(2)
