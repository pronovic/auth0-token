import requests
from fastapi import FastAPI
from starlette.responses import PlainTextResponse

from auth0token.auth0 import get_access_token_endpoint, get_access_token_endpoint_params

APP = FastAPI(docs_url=None, redoc_url=None)  # no Swagger or ReDoc endpoints


@APP.get("/localtoken/callback")
def token_callback(state: str, code: str) -> PlainTextResponse:
    r = requests.post(url=get_access_token_endpoint(), data=get_access_token_endpoint_params(code, state), timeout=10)
    r.raise_for_status()
    return PlainTextResponse(r.json()["access_token"])
