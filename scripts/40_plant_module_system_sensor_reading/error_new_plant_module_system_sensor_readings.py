#!/usr/bin/env python3

#import concurrent.futures
import threading
import random
import httpx
import logging
import sys
import time
import datetime
from new_plant_module_system_sensor_readings import gen_data, main


URL: str = 'http://127.0.0.1:8080/plant_module_system_sensor_reading'
TOKEN: str = 'hello-0-a'

logging.basicConfig(level=logging.INFO)

main(errors=True)
print('starting errors...')
while True:
    # Abbiamo bisogno di letture attuali.
    data = gen_data(readings_per_plant_module_system=1, hours_diff=0)

    for d in data:
        # Simulazione errori payload.
        # Caso 1 per modulo impianto 1.
        # Rinominiamo una chiave del dizionario e ne cancelliamo un'altra.
        if d['plant_module_system_id'] == 1:
            d['voltagee'] = d.pop('voltage')
            del d['current']

        # Caso 2 per modulo impianto 2.
        # Vedere file ../41_.../error_....py

        # Caso 3 per modulo impianto 3.
        if d['plant_module_system_id'] == 3:
            d['ampere'] = d.pop('current')
        # Fine simulazioni errori.

        # Evitiamo di gestire l'errore, lo stampiamo solo sul terminale.
        try:
            response: str = httpx.post(
                URL,
                json=d,
                headers={
                    'Authorization': f'Bearer {TOKEN}',
                }
            )
            logging.info(response.text)
            print(response.text)
            response.raise_for_status()
        except httpx.RequestError as exc:
            logging.error(exc)
        except Exception as exc:
            logging.error(exc)
            print(exc)

        time.sleep(4)
