#!/usr/bin/env python3

import random
import httpx
import logging
import sys
import time
import datetime
from new_plant_battery_system_sensor_readings import gen_data, main


URL: str = 'http://127.0.0.1:8080/plant_battery_system_sensor_reading'
TOKEN: str = 'hello-0-a'

logging.basicConfig(level=logging.INFO)

main(errors=True)
while True:
    # Ho bisogno di letture attuali.
    data = gen_data(readings_per_plant_battery_system=1)

    for d in data:
        # Simulazione errore payload.
        # Caso 2 per modulo impianto 2.
        if d['battery_id'] in [3, 4]:
            d['voltage'] = random.uniform(0.001, 2)
            d['current'] = random.uniform(0.001, 0.01)

        # Caso 3 per modulo impianto 3.
        if d['battery_id'] in [5, 6]:
            d['voltage'] = random.uniform(0.001, 0.01)
            d['current'] = random.uniform(0.05, 0.08)
        # Fine simulazione errori

        # Evitiamo di catturare l'errore.
        response: str = httpx.post(
            URL,
            json=d,
            headers={
                'Authorization': f'Bearer {TOKEN}',
            }
        )

        time.sleep(4)
