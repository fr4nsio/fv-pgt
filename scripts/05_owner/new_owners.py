#!/usr/bin/env python3

import httpx
import logging
import sys

OWNERS: list[dict] = [
        {'first_name': 'Mario', 'last_name': 'Rossi'},
        {'first_name': 'Giulio', 'last_name': 'Bianchi'},
        {'first_name': 'Ferrari', 'last_name': ''},
]
URL: str = 'http://127.0.0.1:8080/owner'
TOKEN: str = 'dummy'

logging.basicConfig(level=logging.INFO)


for owner in OWNERS:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=owner,
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
