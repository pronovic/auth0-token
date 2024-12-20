# Auth0 JWT Token Utilities

[![Test Suite](https://github.com/pronovic/auth0-token/workflows/Test%20Suite/badge.svg)](https://github.com/auth0-token/actions?query=workflow%3A%22Test+Suite%22)
[![Poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

_Developer documentation is found in [DEVELOPER.md](DEVELOPER.md).  See that
file for notes about how the code is structured, how to set up a development
environment, etc._

When you're developing a new web application that relies on JWT tokens, one of
the more frustrating things is that it can be hard to get a usable JWT.  Either
you don't have a running web application yet, or the JWT isn't easily
available, or you need a token for a user that can't easily log into the web
application right now, etc.  There is `auth0 test token <client-id>`, but that
isn't necessarily helpful in all situations.

This is a quick-and-dirty workaround to that problem, inspired by
the [auth-code-flow](https://pypi.org/project/auth-code-flow/0.2.0/) tutorial.
It's not pretty, but it does work, and it does save time.  I've written it
for use on my Macbook, but it may work on other platforms.

Requirements are minimal:

- You must have Python >= 3.11 installed, plus [pipx](https://github.com/pypa/pipx)
- You must have Firefox installed and on your `$PATH`
- Your Auth0 application (under **Applications > Applications**) must have the following allowed redirect URL:

```
http://localhost:35000/localtoken/callback
```

First, download the wheel from the [latest release](https://github.com/pronovic/auth0-token/releases/latest)
and then install using pipx:

```
pipx install auth0_token-0.1.0-py3-none-any.whl
```

Next, prepare an environment file (i.e. `envfile`) that describes your Auth0 configuration.  These are the required variables:

```bash
BASE_URI = "https://my-tenant.us.auth0.com"
AUDIENCE = "my-api-audience"
CLIENT_ID = "my-client-id"
CLIENT_SECRET = "my-client-secret"
```

All of these values are easy to find in Auth0:

- for `my-tenant`, substitute the name of your Auth0 tenant
- for `my-api-audience`, substitute the _API Audience_ associated with your API (under **Applications > APIs**)
- for `my-client-id` and `my-client-secret`, substitute the values from your application (under **Applications > Applications**)

There are also two optional variables:

```
CONNECTION = "my-db"
ORGANIZATION_ID = "my-organization-id"
```

If you have your client configured with an organization prompt (you've selected
_Prompt for Organization_ on the application's **Organizations** tab), then the
`CONNECTION` variable _must_ be omitted.

If you have your client configured with exactly one authentication data source
on the application's **Connections** tab, then the `CONNECTION` variable is
optional.  Otherwise, specify the name of the authentication data source you
want to log in with.  (Strictly speaking, Auth0 will pick a default
authentication data source if you don't provide one, but it might not be the
one you want.)

If you have your client configured with an organization prompt (you've selected
_Prompt for Organization_ on the application's **Organizations** tab), then you
can optionally provide `ORGANIZATION_ID` here so you don't have to enter the
organization name in the web flow every time.  Note that this is the Auth0
organization identifier (like `org_xxxxxxxxxxxxxxxx`), not the lower-case name
that you would enter in the web flow.

Once your environment file exists, you can run the `retrieve` command, which looks
like this:

```
$ auth0token retrieve --env envfile
Waiting 60 seconds for login process  [####################################]  100%          
Login process completed; check Firefox for the access token, and then quit
```

The `retrieve` command coordinates the 
OAuth2 [Authorization Code Flow](https://auth0.com/docs/get-started/authentication-and-authorization-flow), submitting
the correct requests to Auth0 and handling the required callback interaction.

This is done by starting an ephemeral uvicorn server to provide the callback
endpoint, plus a private Firefox browser to handle the web UI aspects of the
flow.  From within the script, we can identify that the login flow is complete,
because the ephemeral uvicorn server will terminate after processing one
request.  At this point, the Firefox browser window will contain a plaintext
JWT access token.  Copy the token out of the browser and then quit.

> **Note:** Annoyingly, it doesn't work very well to run the command multiple
> times if you don't quit Firefox in between &mdash; something to do with how
> I'm starting Firefox in a new private window.  To work around this, when you
> run the `retrieve` command, any leftover Firefox window will be killed.
> Other unrelated Firefox windows will be ignored.
