# Flask MVC Template


[POSTMAN SCRIPT LINK](https://www.postman.com/bread-van-a2/workspace/bread-van-a2-workspace/collection/42730042-07a37cd7-1571-4fc4-924d-ad20047b8dfc?action=share&creator=42730042&active-environment=42730042-cb763b2a-2885-496f-aaef-037885c4224e)
USE THE BREAD VAN API PUBBLEZ'S FORK COLLECTION TO RUN not the Bread Van API collection.


[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/uwidcit/flaskmvc)  
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/uwidcit/flaskmvc)

![Tests](https://github.com/uwidcit/flaskmvc/actions/workflows/dev.yml/badge.svg)

A template for flask applications structured in the Model View Controller pattern. Demo: https://dcit-flaskmvc.herokuapp.com/. Postman Collection: https://documenter.getpostman.com/view/583570/2s83zcTnEJ

# Dependencies

* Python 3 and pip
* Packages listed in requirements.txt

# Installing Dependencies

```bash
pip install -r requirements.txt
```

# Configuration Management

Configuration information such as the database URL/port, credentials, API keys, etc. are supplied to the application via a config file or environment variables. Do not store production secrets in the repository.

## In Development

When running the project in development the app is configured via App/default_config.py. By default it uses a sqlite database.

default_config.py

```python
SQLALCHEMY_DATABASE_URI = "sqlite:///temp-database.db"
SECRET_KEY = "secret key"
JWT_ACCESS_TOKEN_EXPIRES = 7
ENV = "DEVELOPMENT"
```

These values are imported in config.load_config().

## In Production

When deploying to production/staging pass configuration via environment settings in your platform (for example, Render dashboard).

# Flask Commands

wsgi.py exposes custom Flask CLI commands (AppGroup). Example of adding a user command to wsgi.py:

```python
# inside wsgi.py

user_cli = AppGroup('user', help='User object commands')

@user_cli.cli.command("create-user")
@click.argument("username")
@click.argument("password")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

app.cli.add_command(user_cli)
```

Run the command with the Flask CLI, providing the group and command name and arguments.

```bash
flask user create bob bobpass
```

# CLI Commands — Usage & Examples

This project exposes several useful CLI commands. Below are concise usage examples. Replace placeholders (for example `username`) with real values.

* Initialize the application database (custom command):

```bash
flask init
```

* Flask-Migrate database workflow (create / migrate / upgrade):

```bash
flask db init
flask db migrate -m "Add new field"
flask db upgrade
```

* Run the user create command defined in wsgi.py (example):

```bash
flask user create alice s3cr3t
```

* Run the project's test commands via the Flask CLI helper (example runs user tests):

```bash
# run all user tests
flask test user

# run only unit tests
flask test user unit

# run only integration tests
flask test user int
```

* Run the development server with Flask (ensure FLASK_APP is set):

Unix / macOS:

```bash
export FLASK_APP=wsgi.py
export FLASK_ENV=development
flask run
```

Windows (PowerShell):

```powershell
$env:FLASK_APP = "wsgi.py"
$env:FLASK_ENV = "development"
flask run
```

Windows (cmd.exe):

```cmd
set FLASK_APP=wsgi.py && set FLASK_ENV=development && flask run
```

* Run the production server with gunicorn (example binding and workers):

```bash
gunicorn wsgi:app -w 4 -b 0.0.0.0:8000
```

Notes:

* On Windows you typically run development servers with the Flask CLI; gunicorn is generally used on Unix-based production servers.
* If you use a virtual environment, activate it before running these commands so the correct Python environment and dependencies are used.

# Transport CLI Commands (Driver & Resident)

All commands are run from your project root (where wsgi.py is located).

**On Windows, use PowerShell or cmd as shown in the general CLI section.**

## Create a Resident

```bash
flask transport create-resident "Alice"
```
Creates a new resident named Alice.

## Create a Driver

```bash
flask transport create-driver "active"
```
Creates a new driver with status "active".

## Create a Stop Request

```bash
flask transport create-stop <resident_id> <drive_id> --street "Main St"
```
Creates a stop request for a resident and drive.
- `<resident_id>`: The ID of the resident (integer)
- `<drive_id>`: The ID of the drive (integer)
- `--street`: (Optional) Override street name

Example:
```bash
flask transport create-stop 1 2 --street "Main St"
```

## Create a Drive for a Driver

```bash
flask transport create-drive <driver_id> --when "2025-09-16T10:00:00" --location "Depot"
```
Creates a new drive for the driver with optional datetime and location.

## Show Driver Schedule

```bash
flask transport driver-schedule <driver_id>
```
Lists all drives for the given driver.

## Show Resident Inbox (Stop Requests)

```bash
flask transport resident-inbox <resident_id> --street "Main St"
```
Shows all stop requests for a resident, optionally filtered by street.

## List All Data

```bash
flask transport list-all-data
```
Prints all users, drivers, drives, residents, and stop requests in the database.

# Running the Project

For development run the Flask development server:

```bash
flask run
```

For production using gunicorn:

```bash
gunicorn wsgi:app
```

# Deploying

You can deploy your version of this app to Render by clicking the Deploy to Render button above.

# Initializing the Database

When connecting to a fresh database ensure the appropriate configuration is set then run:

```bash
flask init
```

# Database Migrations

If changes to the models are made, migrate the database using Flask-Migrate. See the Flask-Migrate documentation for details.

```bash
flask db init
flask db migrate
flask db upgrade
flask db --help
```

# Testing

## Unit & Integration

Unit and Integration tests are defined in the tests/ folder. The project provides CLI helpers in wsgi.py to run test subsets. Example implementation for user tests in wsgi.py:

```python
@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "User"]))
```

Run all user tests:

```bash
flask test user
```

Run the full test suite with pytest:

```bash
pytest
```

## Test Coverage

Generate a coverage report:

```bash
coverage report
```

Generate an HTML coverage report in htmlcov/:

```bash
coverage html
```

# Troubleshooting

## Views 404ing

If newly created views return 404 ensure they are imported and added in App/main.py:

```python
from App.views import (
    user_views,
    index_views
)

views = [
    user_views,
    index_views
]
```

## Cannot Update Workflow file

If you encounter errors when updating GitHub Actions in Gitpod, ensure Gitpod has workflow permissions enabled.

## Database Issues

If you are adding models you may need to migrate the database with the commands shown above. Alternatively you can delete the sqlite database file during development.
