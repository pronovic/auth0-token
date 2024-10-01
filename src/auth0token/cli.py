from multiprocessing import Process
from subprocess import DEVNULL, Popen
from time import sleep

import click
import uvicorn
from click import ClickException
from dotenv import load_dotenv

from auth0token.auth0 import PORT, SERVER, get_authorization_endpoint
from auth0token.server import callback_called


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(package_name="auth0token", prog_name="auth0token")
def auth0token() -> None:
    """Auth0 token utilities."""


@auth0token.command()
@click.option(
    "--wait-sec",
    "-w",
    "wait_sec",
    metavar="<wait-sec>",
    default=60,
    help="Seconds to wait for login to complete",
)
@click.option(
    "--env",
    "-e",
    "envfile",
    metavar="<envfile>",
    default=".env",
    help="Path to env file on disk, default '.env'",
)
def retrieve(wait_sec: int, envfile: str) -> None:
    """
    Retrieve an Auth0 token for an application and API.

    The env file must contain the following variables:

        \b
        BASE_URI = "https://<tenant>.us.auth0.com"
        CONNECTION = "<database-connection-name>"
        AUDIENCE = "<api-audience>"
        CLIENT_ID = "<client-id>"
        CLIENT_SECRET = "<client-secret>"

    If you have only one database connection, then the CONNECTION
    variable isn't necessary.
    """
    load_dotenv(envfile)

    server = Process(
        target=uvicorn.run,
        args=["auth0token.server:APP"],
        kwargs={"host": SERVER, "port": PORT, "log_level": "error", "env_file": envfile},
        daemon=True,
    )
    server.start()
    sleep(1)

    # TODO: create firefox profile auth0token

    cmdline = ["firefox", "-foreground", "-new-instance", "-P", "auth0token", "-private-window", get_authorization_endpoint()]
    Popen(cmdline, close_fds=True, start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)

    with click.progressbar(length=wait_sec, label=f"Waiting {wait_sec} seconds for login process") as bar:
        attempts = 0
        while attempts < wait_sec:
            click.echo("inside progressbar, CALLED=%s" % callback_called())
            if callback_called():
                bar.update(wait_sec)
                break
            else:
                attempts += 1
                bar.update(1)
                sleep(1)
    if not callback_called():
        raise ClickException(f"Login process did not complete after {wait_sec} seconds")

    server.terminate()
