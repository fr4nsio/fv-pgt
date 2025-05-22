#!/usr/bin/env python3

import httpx
import logging
import sys
import datetime
import random
import time


def create_sensor_reading(sensor_reading_range: dict, plant_id: int, plant_module_system_id: int, is_dc: bool, hours_diff: int, no_alarm_percent_probability: float = 75.0) -> dict:

    if is_dc:
        frequency = 0.0
    else:
        frequency: float = random.uniform(
             sensor_reading_range[plant_id]['frequency']['lower'],
             sensor_reading_range[plant_id]['frequency']['upper']
        )

    if frequency == 0.0:
        voltage = random.uniform(
            sensor_reading_range[plant_id]['voltage']['dc']['lower'],
            sensor_reading_range[plant_id]['voltage']['dc']['upper']
        )
        current = random.uniform(
            sensor_reading_range[plant_id]['current']['dc']['lower'],
            sensor_reading_range[plant_id]['current']['dc']['upper']
        )
    else:
        voltage = random.uniform(
            sensor_reading_range[plant_id]['voltage']['ac']['lower'],
            sensor_reading_range[plant_id]['voltage']['ac']['upper']
        )
        current = random.uniform(
            sensor_reading_range[plant_id]['current']['ac']['lower'],
            sensor_reading_range[plant_id]['current']['ac']['upper']
        )

    alarm_codes: list[str] = ['-01', '00', '01', '02', '03', '04']

    # Probabilità pesata.
    normalized_no_alarm_probability: float = no_alarm_percent_probability / 100
    remaining_slots: int = len(alarm_codes) - 1
    alarm_probability = (1 - normalized_no_alarm_probability) / (len(alarm_codes) - 1)
    weights: list[int] = [normalized_no_alarm_probability] + [alarm_probability] * remaining_slots

    # Dobbiamo passare il timestamp non in UTC ma in formato locale.
    # Ignoriamo le frazioni di secondo
    timestamp: datetime.datetime = (datetime.datetime.now() - datetime.timedelta(hours=hours_diff)).isoformat()[:19]

    return {
        'voltage': voltage,
        'current': current,
        'frequency': frequency,
        'timestamp': timestamp,
        'plant_module_system_id': plant_module_system_id,

        # Seleziona uno dei possibili codici di allarme. '-01' significa
        # assenza di allarme. 2% probabilità che ci sia uno degli allarmi.
        'alarm_code': random.choices(alarm_codes, weights, k=1)[0]
    }


# COdifichiamo qui direttamente i valori: in realtà bisognerebbe usare l'API
sensor_reading_range = {
    1: {
        'voltage': {
            'dc': {
                'lower': 47.0,
                'upper': 319.0,
            },
            'ac': {
                'lower': 230.0,
                'upper': 245.0,
            },
        },
        'current': {
            'dc': {
                'lower': 10.1,
                'upper': 20.0,
            },
            'ac': {
                'lower': 13.0,
                'upper': 17.0,
            },
        },
        'frequency': {
            'lower': 45.0,
            'upper': 51.0,
        },
    },
    2: {
        'voltage': {
            'dc': {
                'lower': 47.0,
                'upper': 319.0,
            },
            'ac': {
                'lower': 230.0,
                'upper': 245.0,
            },
        },
        'current': {
            'dc': {
                'lower': 10.1,
                'upper': 20.0,
            },
            'ac': {
                'lower': 13.0,
                'upper': 17.0,
            },
        },
        'frequency': {
            'lower': 45.0,
            'upper': 51.0,
        },
    },
    3: {
        'voltage': {
            'dc': {
                'lower': 300.0,
                'upper': 600.0,
            },
            'ac': {
                'lower': 200.0,
                'upper': 400.0,
            },
        },
        'current': {
            'dc': {
                'lower': 16.0,
                'upper': 32.5,
            },
            'ac': {
                'lower': 10.0,
                'upper': 12.0,
            },
        },
        'frequency': {
            'lower': 45.0,
            'upper': 66.0,
        },
    },
}


def gen_data(readings_per_plant_module_system: int = 24, hours_diff: int = sys.maxsize):
    # plant_id e plant_module_system_id sono uguali se gli script non vengono
    # modificati.
    data: list[dict] = []

    for j in range(1, 4):
        for i in range(0, readings_per_plant_module_system):
            if hours_diff != sys.maxsize:
                h_diff = hours_diff
            else:
                h_diff = i

            dc_reading = create_sensor_reading(
                sensor_reading_range, j, j, True, h_diff
            )
            ac_reading = create_sensor_reading(
                sensor_reading_range, j, j, False, h_diff
            )

            data.append(dc_reading)
            data.append(ac_reading)

    return data


def main(errors: bool = False):
    URL: str = 'http://127.0.0.1:8080/plant_module_system_sensor_reading'

    # See the 06-* scripts.
    TOKEN: str = 'hello-0-a'

    logging.basicConfig(level=logging.INFO)

    PLANT_MODULE_SYSTEM_SENSOR_READINGS: list[dict] = gen_data()
    error_counter: int = 0

    for plant_module_system_sensor_reading in PLANT_MODULE_SYSTEM_SENSOR_READINGS:

        # Per la simulazione di errori non popoliamo i dati del primo impianto,
        # lasciamo che sia lo script error_new_plant_module_system_sensor_readings.py
        # a farlo.
        if errors and plant_module_system_sensor_reading['plant_module_system_id'] in [1, 3]:
            continue

        response: str = ''
        try:
            response = httpx.post(
                URL,
                json=plant_module_system_sensor_reading,
                headers={
                    'Authorization': f'Bearer {TOKEN}',
                }
            )
            print(response.text)
            response.raise_for_status()
        except httpx.RequestError as exc:
            logging.error(f'An error occurred while requesting {exc.request.url!r}.')
            logging.error(exc)
            error_counter += 1

        if error_counter >= 2:
            logging.error('too many errors: quitting')
            sys.exit(1)

        # Un po' di timeout per evitare di sovraccaricare il server di sviluppo.
        time.sleep(0.1)


if __name__ == '__main__':
    main()
