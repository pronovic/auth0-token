# pylint: disable=consider-using-with:
import os
from multiprocessing import Process
from subprocess import DEVNULL, Popen
from time import sleep

import click
import psutil
import uvicorn
from click import ClickException
from dotenv import load_dotenv
from environs import env
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from auth0token.auth0 import PORT, SERVER, get_authorization_endpoint

RENDER_DELAY = 5  # wait for up to 5 seconds for the login page to render


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def auth0token() -> None:
    """Auth0 JWT token utilities."""


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
    "env_file",
    metavar="<env-file>",
    default=".env",
    help="Path to env file on disk, default '.env'",
)
def retrieve(wait_sec: int, env_file: str) -> None:
    """
    Manually retrieve an Auth0 JWT access token.

    This coordinates the OIDC Authorization Code flow, submitting the correct
    requests to Auth0 and handling the required callback interaction.  This is
    done by starting an ephemeral uvicorn server to provide the callback
    endpoint and a private Firefox browser to handle the web UI aspects of the
    flow.

    This command expects you to manually log into Auth0 via the browser window.
    Wait for Firefox to start, log in with your credentials, and then capture
    the access token out of the browser window.  Then quit Firefox.

    Your Auth0 application (under Applications > Applications) must have the
    following allowed redirect URL:

        \b
        http://localhost:35000/localtoken/callback

    The environment file must contain the following variables:

        \b
        BASE_URI = "https://<tenant>.us.auth0.com"
        AUDIENCE = "<api-audience>"
        CLIENT_ID = "<client-id>"
        CLIENT_SECRET = "<client-secret>"

    There are two optional variables:

        \b
        CONNECTION = "<database-connection-name>"
        ORGANIZATION_ID = "<organization-id>"

    If you have your client configured with an organization prompt, then the
    CONNECTION variable must be omitted.  If you have your client configured
    with exactly one authentication data source, then the CONNECTION variable
    is optional.  Otherwise, specify the name of the authentication data source
    you want to log in with.

    If you have your client configured with an organization prompt, then you
    can optionally provide ORGANIZATION_ID here so you don't have to enter the
    organization name in the web flow every time.  Note that this is the Auth0
    organization identifier, not the lower-case name that you would enter in the
    web flow.

    If you use "-" for the location of your envfile, then the expected variables
    are assumed to be in your environment already and no envfile is sourced.
    """
    server_args = {
        "host": SERVER,
        "port": PORT,
        "log_level": "error",
        "limit_max_requests": 1,
    }

    if env_file != "-":
        server_args["env_file"] = env_file
        load_dotenv(env_file)

    server = Process(
        target=uvicorn.run,
        args=["auth0token.api:APP"],
        kwargs=server_args,
        daemon=True,
    )
    server.start()
    sleep(1)

    # kill any existing Firefox opened by auth0token, which we identify by looking for indicators in the CLI
    # annoyingly, if there is an existing window, then the new window below opens, but doesn't work properly
    for process in psutil.process_iter():
        if process.uids().real == os.getuid() and process.name() == "firefox":
            if "-P auth0token -private-window" in " ".join(process.cmdline()):
                process.kill()
                click.echo("Closed existing auth0token Firefox window that was left open")

    # create a new Firefox profile for use by auth0 token
    cmdline = ["firefox", "-CreateProfile", "auth0token"]
    create = Popen(cmdline, close_fds=True, start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)
    create.wait(5)

    # open a new private Firefox window specfically for use in the login flow
    cmdline = ["firefox", "-foreground", "-new-instance", "-P", "auth0token", "-private-window", get_authorization_endpoint()]
    Popen(cmdline, close_fds=True, start_new_session=True, stdout=DEVNULL, stderr=DEVNULL)

    # noinspection PyUnresolvedReferences
    # make MyPy happy; see https://github.com/pallets/click/issues/2626
    bar: click._termui_impl.ProgressBar[int]

    with click.progressbar(length=wait_sec, label=f"Waiting {wait_sec} seconds for login process") as bar:
        attempts = 0
        while server.is_alive():
            attempts += 1
            if attempts >= wait_sec:
                server.terminate()
                raise ClickException(f"Login process did not complete after {wait_sec} seconds")
            bar.update(1)
            sleep(1)
        bar.update(wait_sec)

    click.echo("Login process completed; check Firefox for the access token, and then quit")


@auth0token.command()
@click.option(
    "--env",
    "-e",
    "env_file",
    metavar="<env-file>",
    default=".env",
    help="Path to env file on disk, default '.env'",
)
def scripted(env_file: str) -> None:
    """
    Automatically retrieve an Auth0 JWT access token.

    This coordinates the OIDC Authorization Code flow, submitting the correct
    requests to Auth0 and handling the required callback interaction.  This is
    done by starting an ephemeral uvicorn server to provide the callback
    endpoint and a private Firefox browser to handle the web UI aspects of the
    flow.

    Interaction with the browser is scripted using selenium.  When the command
    completes, the token will be dumped to stdout.

    Your Auth0 application (under Applications > Applications) must have the
    following allowed redirect URL:

        \b
        http://localhost:35000/localtoken/callback

    The environment file must contain the following variables:

        \b
        BASE_URI = "https://<tenant>.us.auth0.com"
        AUDIENCE = "<api-audience>"
        CLIENT_ID = "<client-id>"
        CLIENT_SECRET = "<client-secret>"
        LOGIN_USERNAME = "<login-username>"
        LOGIN_PASSWORD = "<login-password>"

    There are two optional variables:

        \b
        CONNECTION = "<database-connection-name>"
        ORGANIZATION_ID = "<organization-id>"

    If you have your client configured with an organization prompt, then the
    CONNECTION variable must be omitted.  If you have your client configured
    with exactly one authentication data source, then the CONNECTION variable
    is optional.  Otherwise, specify the name of the authentication data source
    you want to log in with.

    If you have your client configured with an organization prompt, then you
    can optionally provide ORGANIZATION_ID here so you don't have to enter the
    organization name in the web flow every time.  Note that this is the Auth0
    organization identifier, not the lower-case name that you would enter in the
    web flow.

    If you use "-" for the location of your envfile, then the expected variables
    are assumed to be in your environment already and no envfile is sourced.
    """
    server_args = {
        "host": SERVER,
        "port": PORT,
        "log_level": "error",
        "limit_max_requests": 1,
    }

    if env_file != "-":
        server_args["env_file"] = env_file
        load_dotenv(env_file)

    server = Process(
        target=uvicorn.run,
        args=["auth0token.api:APP"],
        kwargs=server_args,
        daemon=True,
    )
    server.start()
    sleep(1)

    login_username = env.str("LOGIN_USERNAME")
    login_password = env.str("LOGIN_PASSWORD")

    browser = webdriver.Firefox()
    browser.get(get_authorization_endpoint())

    def wait_by_id(identifier: str) -> WebElement:
        WebDriverWait(browser, RENDER_DELAY).until(EC.presence_of_element_located((By.ID, identifier)))
        return browser.find_element(By.ID, identifier)

    def wait_by_name(name: str) -> WebElement:
        WebDriverWait(browser, RENDER_DELAY).until(EC.presence_of_element_located((By.NAME, name)))
        return browser.find_element(By.NAME, name)

    def wait_by_xpath(xpath: str) -> WebElement:
        WebDriverWait(browser, RENDER_DELAY).until(EC.presence_of_element_located((By.XPATH, xpath)))
        return browser.find_element(By.XPATH, xpath)

    username = wait_by_id("username")
    submit = wait_by_name("action")
    username.click()
    username.clear()
    username.send_keys(login_username)
    submit.click()

    password = wait_by_id("password")
    submit = wait_by_name("action")
    password.click()
    password.clear()
    password.send_keys(login_password)
    submit.click()

    content = wait_by_xpath("//pre")
    token = content.get_attribute("innerHTML")
    click.echo(token)

    browser.quit()
