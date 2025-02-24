import os
from typing import Dict
from urllib.parse import urlencode
from uuid import uuid4

import click
from environs import env

SERVER = "localhost"
PORT = 35000


def get_authorization_endpoint() -> str:
    state = str(uuid4())
    return (
        env.str("BASE_URI", default="BASE_URI")
        + env.str("AUTHORIZATION_PATH", default="/authorize")
        + "?"
        + urlencode(get_authorization_endpoint_params(state=state))
    )


def get_authorization_endpoint_params(state: str) -> Dict[str, str]:
    params = {
        "client_id": env.str("CLIENT_ID", default="CLIENT_ID"),
        "redirect_uri": env.str("REDIRECT_URI", default=f"http://{SERVER}:{PORT}/localtoken/callback"),
        "response_type": "code",
        "scope": env.str("SCOPE", default="openid email profile"),
        "state": state,
        "audience": env.str("AUDIENCE", default="AUDIENCE"),
    }

    if env.str("ORGANIZATION_ID", default=None):
        if env.str("CONNECTION", default=None):
            raise click.UsageError("Use either $ORGANIZATION_ID or $CONNECTION, not both")
        params["organization"] = env.str("ORGANIZATION_ID", default="unset")
    elif env.str("CONNECTION", default=None):
        params["connection"] = env.str("CONNECTION", default="unset")

    return params


def get_access_token_endpoint() -> str:
    return env.str("BASE_URI", default="BASE_URI") + os.getenv("ACCESS_TOKEN_PATH", default="/oauth/token")


def get_access_token_endpoint_params(code: str, state: str) -> Dict[str, str]:
    return {
        "code": code,
        "client_id": env.str("CLIENT_ID", default="CLIENT_ID"),
        "client_secret": env.str("CLIENT_SECRET", default="CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "redirect_uri": env.str("REDIRECT_URI", default=f"http://{SERVER}:{PORT}/localtoken/callback"),
        "state": state,
    }
