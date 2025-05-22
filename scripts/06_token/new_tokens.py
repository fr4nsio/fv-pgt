#!/usr/bin/env python3

import httpx
import logging
import sys

TOKENS: list[dict] = [
    {'api_token': 'hello-0-a'},
    {'api_token': 'hello-1-b'},
    {'api_token': 'hello-2-c'},
]
AUTH=('admin0', 'password0')
URL: str = 'http://127.0.0.1:8080/token'

logging.basicConfig(level=logging.INFO)


for token in TOKENS:
    response: str = ''
    try:
        response = httpx.post(
            URL,
            json=token,
            auth=AUTH,
        )
        print(response.text)
        response.raise_for_status()
    except httpx.RequestError as exc:
        logging.error(f'An error occurred while requesting {exc.request.url!r}.')
        logging.error(exc)
        sys.exit(1)
