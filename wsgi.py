import click, sys
from flask import Flask
from flask.cli import with_appcontext, AppGroup
from flask_jwt_extended import JWTManager
import json

from App.views import views
'''from App.views.transport import transport_views
from App.views.user import user_views
from App.views.auth import auth_views'''

from App.models import User, Driver, Resident

from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize,
                              create_resident, create_driver, create_stop_request,
                              create_drive, get_driver_schedule, get_resident_inbox, print_all_data )
from App.controllers.admin import print_users, print_drivers, print_drives, print_residents, print_stop_requests


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

jwt = JWTManager(app)

@jwt.user_identity_loader
def user_identity_lookup(user):
    if isinstance(user, dict):
        return user  # Already in correct form

    role = "user"
    if isinstance(user, Driver):
        role = "driver"
    elif isinstance(user, Resident):
        role = "resident"

    return {"id": user.id, "role": role}

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]  # The dict we stored earlier
    user_id = identity.get("id")
    role = identity.get("role")

    if role == "driver":
        return db.session.get(Driver, user_id)
    elif role == "resident":
        return db.session.get(Resident, user_id)
    else:
        return db.session.get(User, user_id)
############
if __name__ == "__main__":
    app.run(debug=True)


# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    initialize()
    print('database intialized')

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

'''
Resident & Driver Commands Grouped under 'transport'
'''
transport_cli = AppGroup('transport', help='Resident and Driver object commands')

@transport_cli.command('create-resident', help='Create a resident')
@click.argument('name', default=None)
def create_resident_command(name):
    r = create_resident(name)
    print(f'Resident created: id={r.id} name={r.name}')

@transport_cli.command('create-driver', help='Create a driver')
@click.argument('status', default=None)
def create_driver_command(status):
    d = create_driver(status)
    print(f'Driver created: id={d.id} status={d.status}')

@transport_cli.command('create-stop', help='Create a stop request for an existing drive and resident')
@click.argument('resident_id', type=int)
@click.argument('drive_id', type=int)
@click.option('--street', default=None, help='Optional street name override; defaults to resident.street')
def create_stop_command(resident_id, drive_id, street):
    sr = create_stop_request(resident_id, drive_id, street)
    if sr:
        print(f'StopRequest created: id={sr.id} resident={sr.requestee_id} drive={sr.drive_id} street="{sr.street_name}"')
    else:
        print('Resident or Drive not found')

@transport_cli.command('create-drive', help='Create a new drive for a driver')
@click.argument('driver_id', type=int)
@click.option('--when', default=None, help='ISO datetime string for drive time (optional)')
@click.option('--location', default=None, help='Current location string (optional)')
def create_drive_command(driver_id, when, location):
    drive = create_drive(driver_id, when=when, current_location=location)
    if drive:
        print(f'Drive created: id={drive.id} driver_id={drive.driver_id} datetime={drive.datetime} location={drive.current_location}')
    else:
        print('Driver not found or error')

@transport_cli.command('driver-schedule', help='Show driver schedule (drives)')
@click.argument('driver_id', type=int)
def driver_schedule_command(driver_id):
    schedule = get_driver_schedule(driver_id)
    if not schedule:
        print('No schedule or driver not found')
        return
    for d in schedule:
        print(f'Drive id={d.id} datetime={d.datetime} stops={[s.id for s in d.stops]}')

@transport_cli.command('resident-inbox', help='Show resident inbox of stop requests')
@click.argument('resident_id', type=int)
@click.option('--street', default=None, help='Optional street name filter')
def resident_inbox_command(resident_id, street):
    inbox = get_resident_inbox(resident_id, street)
    if not inbox:
        print('No stop requests or resident not found')
        return
    for sr in inbox:
        print(f'StopRequest id={sr.id} street="{sr.street_name}" resident_id={sr.requestee_id} created_at={sr.created_at}')

@transport_cli.command('list-all-data', help='Pretty-print all data (users, drivers, drives, residents, stop requests)')
def list_all_data_command():
    print_all_data()

# New CLI commands for printing individual tables
@transport_cli.command('print-users', help='Pretty-print only the users table')
def print_users_command():
    print_users()

@transport_cli.command('print-drivers', help='Pretty-print only the drivers table')
def print_drivers_command():
    print_drivers()

@transport_cli.command('print-drives', help='Pretty-print only the drives table')
def print_drives_command():
    print_drives()

@transport_cli.command('print-residents', help='Pretty-print only the residents table')
def print_residents_command():
    print_residents()

@transport_cli.command('print-stop-requests', help='Pretty-print only the stop requests table')
def print_stop_requests_command():
    print_stop_requests()

app.cli.add_command(transport_cli)

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    import importlib
    try:
        pytest = importlib.import_module('pytest')
    except Exception:
        print('pytest is not installed in this environment')
        return
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)