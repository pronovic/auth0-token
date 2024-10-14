import os
from typing import Dict
from urllib.parse import urlencode
from uuid import uuid4

import click

SERVER = "localhost"
PORT = 35000


def get_authorization_endpoint() -> str:
    state = str(uuid4())
    return (
        os.getenv("BASE_URI", default="BASE_URI")
        + os.getenv("AUTHORIZATION_PATH", default="/authorize")
        + "?"
        + urlencode(get_authorization_endpoint_params(state=state))
    )


def get_authorization_endpoint_params(state: str) -> Dict[str, str]:
    params = {
        "client_id": os.getenv("CLIENT_ID", default="CLIENT_ID"),
        "redirect_uri": os.getenv("REDIRECT_URI", default=f"http://{SERVER}:{PORT}/localtoken/callback"),
        "response_type": "code",
        "scope": os.getenv("SCOPE", default="openid email profile"),
        "state": state,
        "audience": os.getenv("AUDIENCE", default="AUDIENCE"),
    }

    if os.getenv("ORGANIZATION_ID", default=None):
        if os.getenv("CONNECTION", default=None):
            raise click.UsageError("Use either $ORGANIZATION_ID or $CONNECTION, not both")
        params["organization"] = os.getenv("ORGANIZATION_ID", default="unset")
    elif os.getenv("CONNECTION", default=None):
        params["connection"] = os.getenv("CONNECTION", default="unset")

    return params


def get_access_token_endpoint() -> str:
    return os.getenv("BASE_URI", default="BASE_URI") + os.getenv("ACCESS_TOKEN_PATH", default="/oauth/token")


def get_access_token_endpoint_params(code: str, state: str) -> Dict[str, str]:
    return {
        "code": code,
        "client_id": os.getenv("CLIENT_ID", default="CLIENT_ID"),
        "client_secret": os.getenv("CLIENT_SECRET", default="CLIENT_SECRET"),
        "grant_type": "authorization_code",
        "redirect_uri": os.getenv("REDIRECT_URI", default=f"http://{SERVER}:{PORT}/localtoken/callback"),
        "state": state,
    }
