#!/usr/bin/env python3

import httpx
import logging
import sys
import datetime
import random
import time


def create_sensor_reading(sensor_reading_range: dict, battery_id: int, hours_diff: int) -> dict:
    voltage = random.uniform(
        sensor_reading_range[battery_id]['voltage']['lower'],
        sensor_reading_range[battery_id]['voltage']['upper']
    )
    current = random.uniform(
        sensor_reading_range[battery_id]['current']['lower'],
        sensor_reading_range[battery_id]['current']['upper']
    )

    return {
        'voltage': voltage,
        'current': current,
        'frequency': 0.0,
        'timestamp': (datetime.datetime.now() - datetime.timedelta(hours=hours_diff)).isoformat()[:19],
        'battery_id': battery_id
    }


# Codifichiamo qui direttamente i valori: in realtà bisognerebbe usare l'API
sensor_reading_range = {
    1: {
        'voltage': {
            'lower': 49.0,
            'upper': 50.0,
        },
        'current': {
            'lower': 10.0,
            'upper': 18.0,
        },
    },
    2: {
        'voltage': {
            'lower': 49.0,
            'upper': 50.0,
        },
        'current': {
            'lower': 13.0,
            'upper': 60.0,
        },
    },
    3: {
        'voltage': {
            'lower': 49.0,
            'upper': 50.0,
        },
        'current': {
            'lower': 10.0,
            'upper': 18.0,
        },
    },
    4: {
        'voltage': {
            'lower': 49.0,
            'upper': 50.0,
        },
        'current': {
            'lower': 13.0,
            'upper': 60.0,
        },
    },
    5: {
        'voltage': {
            'lower': 160.0,
            'upper': 600.0,
        },
        'current': {
            'lower': 0.1,
            'upper': 18.0,
        },
    },
    6: {
        'voltage': {
            'lower': 160.0,
            'upper': 600.0,
        },
        'current': {
            'lower': 20.0,
            'upper': 25.0,
        },
    },
}


def gen_data(readings_per_plant_battery_system: int = 4):
    # plant_id e plant_module_system_id sono uguali se gli script non vengono
    # modificati.
    data: list[dict] = []

    # Abbiamo 3 impianti, quindi 6 batterie.
    for j in range(1, 7):
        for i in range(0, readings_per_plant_battery_system):
            r0 = create_sensor_reading(
                sensor_reading_range, j, i
            )
            r1 = create_sensor_reading(
                sensor_reading_range, j, i
            )

            data.append(r0)
            data.append(r1)

    return data


def main(errors: bool = False):
    PLANT_BATTERY_SYSTEM_SENSOR_READINGS: list[dict] = gen_data()
    URL: str = 'http://127.0.0.1:8080/plant_battery_system_sensor_reading'

    # See the 06-* scripts.
    TOKEN: str = 'hello-0-a'

    logging.basicConfig(level=logging.INFO)

    for plant_battery_system_sensor_reading in PLANT_BATTERY_SYSTEM_SENSOR_READINGS:

        # Per la simulazione di errori non popoliamo i dati della batteria 3 e 4
        # corrispondenti al secondo impianto, lasciamo che sia lo script
        # error_new_battery_module_system_sensor_readings.py a farlo.
        if errors and plant_battery_system_sensor_reading['battery_id'] in [3, 4, 5, 6]:
            continue

        response: str = ''
        try:
            response = httpx.post(
                URL,
                json=plant_battery_system_sensor_reading,
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

        # Un po' di timeout per evitare di sovraccaricare il server di sviluppo.
        time.sleep(0.1)


if __name__ == '__main__':
    main()
