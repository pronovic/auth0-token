# Auth0 JWT Token Utilities

[![license](https://img.shields.io/pypi/l/auth0-token.svg)](https://github.com/pronovic/auth0-token/blob/master/LICENSE)
[![python](https://img.shields.io/pypi/pyversions/auth0-token.svg)](https://pypi.org/project/auth0-token/)
[![Test Suite](https://github.com/pronovic/auth0-token/workflows/Test%20Suite/badge.svg)](https://github.com/auth0-token/actions?query=workflow%3A%22Test+Suite%22)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

_Developer documentation is found in [DEVELOPER.md](DEVELOPER.md).  See that
file for notes about how the code is structured, how to set up a development
environment, etc._

When you're developing a new web application that relies on JWT tokens, one of
the more frustrating things is that it can be hard to get a usable JWT.  Either
you don't have a running web application yet, or the JWT isn't easily
available, or you need a token for a user that can't easily log into the web
application right now, etc.

This is a quick-and-dirty workaround to that problem, inspired by
the [auth-code-flow](https://pypi.org/project/auth-code-flow/0.2.0/) tutorial.
It's not pretty, but it does work, and it does save time.

Requiements are minimal:

- You must have Python >= 3.12 installed
- You must have Firefox installed and on your `$PATH`
- Your Auth0 application (under **Applications > Applications**) must have the following as an allowed redirect URL:

```
http://localhost:35000/localtoken/callback
```

First, download install the wheel from the [latest release](https://github.com/pronovic/auth0-token/releases/latest)
and then install using pipx:

```
pipx install auth0_token-0.1.0-py3-none-any.whl
```

Next, prepare an environment file (i.e. `envfile`) that describes your Auth0 configuration:

```bash
BASE_URI = "https://my-tenant.us.auth0.com"
CONNECTION = "my-db"
AUDIENCE = "my-api-audience"
CLIENT_ID = "my-client-id"
CLIENT_SECRET = "my-client-secret"
```

All of these things are easy to find in Auth0

- for `my-tenant`, substitute the name of your Auth0 tenant
- for `my-db`, subtitute the name of your user database (under **Authentication > Database**)
- for `my-api-audience`, substitute the _API Audience_ associated with your API (under **Applications > APIs**)
- for `my-client-id` and `my-client-secret`, substitute the values from your application (under **Applications > Applications**)

Once your environment file exists, you can run the `retrieve` command, which looks
like this:

```
$ auth0token retrieve --env envfile
Waiting 60 seconds for login process  [####################################]  100%          
Login process completed; check Firefox for the access token, and then quit
```

The `retrieve` command coordinates the OAuth2 Authorization Code Flow,
submitting the correct requests to Auth0 and handling the required callback
interaction.  This is done by starting an ephemeral uvicorn server to provide
the callback endpoint and a private Firefox browser to handle the web UI
aspects of the flow.  When the login flow is complete, the Firefox browser will
contain your JWT access token.  Copy the token out of the browser and then
quit.

> **Note:** Annoyingly, it doesn't work very well to run the command multiple
> times if you don't quit Firefox in between &mdash; something to do with how
> I'm starting Firefox in a new private window.
