# Developer Notes

## Packaging and Dependencies

This project uses [UV](https://docs.astral.sh/uv/) to manage Python packaging and dependencies.  Most day-to-day tasks (such as running unit tests from the command line) are orchestrated through UV.

A coding standard is enforced using [Ruff](https://docs.astral.sh/ruff/).  Python 3 type hinting is validated using [MyPy](https://pypi.org/project/mypy/).

## Supported Platforms

I wrote this for use on my Macbook.  It may also work on Linux or Windows, but I haven't tested there.

## Unit Tests

This is a quick-and-dirty hack, not production code.  There are no unit tests. I tested the code manually while trying to figure out a process that would work.

## Pre-Commit Hooks

We rely on pre-commit hooks to ensure that the code is properly-formatted,
clean, and type-safe when it's checked in.  The `run install` step described
below installs the project pre-commit hooks into your repository.  These hooks
are configured in [`.pre-commit-config.yaml`](.pre-commit-config.yaml).

If necessary, you can temporarily disable a hook using Git's `--no-verify`
switch.  However, keep in mind that the CI build on GitHub enforces these
checks, so the build will fail.

## Line Endings

The [`.gitattributes`](.gitattributes) file controls line endings for the files
in this repository.  Instead of relying on automatic behavior, the
`.gitattributes` file forces most files to have UNIX line endings.

## Prerequisites

All prerequisites are managed by UV.  All you need to do install UV itself,
following the [instructions](https://docs.astral.sh/uv/getting-started/installation/).
UV will take care of installing the required Python interpreter and all of the
dependencies.

> **Note:** The development environment (the `run` script, etc.) expects a bash
> shell to be available.  On Windows, it works fine with the standard Git Bash.

## Developer Tasks

The [`run`](run) script provides shortcuts for common developer tasks:

```
$ ./run --help
------------------------------------
Shortcuts for common developer tasks
------------------------------------

Basic tasks:

- run install: Install the Python virtualenv and pre-commit hooks
- run update: Update all dependencies, or a subset passed as arguments
- run outdated: Find top-level dependencies with outdated constraints
- run rebuild: Rebuild all dependencies flagged as no-binary-package
- run outdated: Find top-level dependencies with outdated constraints
- run format: Run the code formatters
- run checks: Run the code checkers
- run build: Build artifacts in the dist/ directory
- run suite: Run the complete test suite, as for the GitHub Actions CI build
- run suite -f: Run a faster version of the test suite, omitting some steps
- run clean: Clean the source tree

Additional tasks:

- run release: Tag and release the code, triggering GHA to publish artifacts
```

## Integration with PyCharm

Currently, I use [PyCharm Community Edition](https://www.jetbrains.com/pycharm/download) as 
my day-to-day IDE.  By integrating the `run` script to execute MyPy and Ruff,
most everything important that can be done from a shell environment can also be
done right in PyCharm.

PyCharm offers a good developer experience.  However, the underlying configuration
on disk mixes together project policy (i.e. preferences about which test runner to
use) with system-specific settings (such as the name and version of the active Python 
interpreter). This makes it impossible to commit complete PyCharm configuration 
to the Git repository.  Instead, the repository contains partial configuration, and 
there are instructions below about how to manually configure the remaining items.

### Prerequisites

Before going any further, make sure sure that you have installed UV and have a
working bash shell.  Then, run the suite and confirm that everything is working:

```
./run suite
```

### Open the Project

Once you have a working shell development environment, **Open** (do not
**Import**) the `auth0-token` directory in PyCharm, then follow the remaining
instructions below.  By using **Open**, the existing `.idea` directory will be
retained and all of the existing settings will be used.

### Interpreter

As a security precaution, PyCharm does not trust any virtual environment
installed within the repository, such as the UV `.venv` directory. In the
status bar on the bottom right, PyCharm will report _No interpreter_.  Click
on this error and select **Add Interpreter**.  In the resulting dialog, click
**Ok** to accept the selected environment, which should be the UV virtual
environment.

### Project Structure

Go to the PyCharm settings and find the `auth0-token` project.  Under **Project
Structure**, mark `src` as a source folder.  In the **Exclude
Files** box, enter the following:

```
LICENSE;NOTICE;PyPI.md;build;dist;out;uv.lock;run;.coverage;.coverage.lcov;.coveragerc;.gitattributes;.github;.gitignore;.htmlcov;.idea;.mypy_cache;.pre-commit-config.yaml;.pytest_cache;.python-version;.readthedocs.yaml;.ruff_cache;.run;.tabignore;.venv;.env*
```

When you're done, click **Ok**.  Then, go to the gear icon in the project panel 
and uncheck **Show Excluded Files**.  This will hide the files and directories 
in the list above.

### Tool Preferences

In the PyCharm settings, go to **Editor > Inspections** and be sure that the
**Project Default** profile is selected.

### External Tools

Optionally, you might want to set up external tools for some of common
developer tasks: code reformatting and the Ruff and MyPy checks.  One nice
advantage of doing this is that you can configure an output filter, which makes
the Ruff linter and MyPy errors clickable.  To set up external tools, go to
PyCharm settings and find **Tools > External Tools**.  Add the tools as
described below.

##### Format Code

|Field|Value|
|-----|-----|
|Name|`Format Code`|
|Description|`Run the Ruff code formatter`|
|Group|`Developer Tools`|
|Program|`$ProjectFileDir$/run`|
|Arguments|`format`|
|Working directory|`$ProjectFileDir$`|
|Synchronize files after execution|_Checked_|
|Open console for tool outout|_Checked_|
|Make console active on message in stdout|_Unchecked_|
|Make console active on message in stderr|_Unchecked_|
|Output filters|_Empty_|

##### Run MyPy Checks

|Field|Value|
|-----|-----|
|Name|`Run MyPy Checks`|
|Description|`Run the MyPy code checks`|
|Group|`Developer Tools`|
|Program|`$ProjectFileDir$/run`|
|Arguments|`mypy`|
|Working directory|`$ProjectFileDir$`|
|Synchronize files after execution|_Unchecked_|
|Open console for tool outout|_Checked_|
|Make console active on message in stdout|_Checked_|
|Make console active on message in stderr|_Checked_|
|Output filters|`$FILE_PATH$:$LINE$`|

##### Run Ruff Linter Checks

|Field|Value|
|-----|-----|
|Name|`Run Ruff Linter`|
|Description|`Run the Ruff linter code checks`|
|Group|`Developer Tools`|
|Program|`$ProjectFileDir$/run`|
|Arguments|`ruff`|
|Working directory|`$ProjectFileDir$`|
|Synchronize files after execution|_Unchecked_|
|Open console for tool outout|_Checked_|
|Make console active on message in stdout|_Checked_|
|Make console active on message in stderr|_Checked_|
|Output filters|`$FILE_PATH$:$LINE$`|

## Release Process

### Code

Code is released to [PyPI](https://pypi.org/project/auth0-token/).  There is a
partially-automated process to publish a new release.

> **Note:** In order to publish code, you must must have push permissions to the
> GitHub repo.

Ensure that you are on the `main` branch.  Releases must always be done from
`main`.

Ensure that the `Changelog` is up-to-date and reflects all of the changes that
will be published.  The top line must show your version as unreleased:

```
Version 0.1.0      unreleased
```

Run the release command:

```
./run release 0.1.0
```

This command updates `NOTICE` and `Changelog` to reflect the release version
and release date, commits those changes, tags the code, and pushes to GitHub.
The new tag triggers a GitHub Actions build that runs the test suite, generates
the artifacts, and finally creates a release from the tag.
