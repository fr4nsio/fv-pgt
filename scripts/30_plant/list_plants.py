#!/usr/bin/env python3

import httpx
import logging
import sys
import pprint

URL: str = 'http://127.0.0.1:8080/plant'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


response: str = ''
try:
    response = httpx.get(
        URL,
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
