from datetime import datetime
from App.models import Driver
from App.database import db

def create_driver(username, password, status=None):
    d = Driver(username=username, password=password, status=status)
    db.session.add(d)
    db.session.commit()
    return d

def get_driver(id):
    return db.session.get(Driver, id)

def create_drive(driver_id, when=None, current_location=None):
    driver = get_driver(driver_id)
    if not driver:
        return None
    return driver.add_drive(when=when, current_location=current_location)

def get_driver_schedule(driver_id):
    driver = get_driver(driver_id)
    if not driver:
        return []
    return list(driver.schedule)
