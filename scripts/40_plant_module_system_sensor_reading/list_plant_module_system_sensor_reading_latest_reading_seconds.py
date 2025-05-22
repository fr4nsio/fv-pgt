#!/usr/bin/env python3

import httpx
import logging
import sys
import pprint

URL: str = 'http://127.0.0.1:8080/plant_module_system_sensor_reading?plant_id=1&latest_reading_seconds=86400'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)

response = httpx.get(
    URL,
    headers={
        'Authorization': f'Bearer {TOKEN}',
    }
)
pprint.pprint(response.json())
