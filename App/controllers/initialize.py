from .user import create_user
from App.database import db

from App.models import Driver, Resident


def initialize():
    # Reset schema
    db.drop_all()
    db.create_all()

    # Create a sample user
    create_user('bob', 'bobpass')

    # Create drivers
    d1 = Driver(username='luca', password='pass123', status='active')
    d2 = Driver(username='honey', password='pass123', status='active')
    db.session.add_all([d1, d2])
    db.session.commit()

    # Create initial drives for drivers (uses Driver.add_drive which commits)
    drive1 = d1.add_drive(current_location='Depot')
    drive2 = d2.add_drive(current_location='North Route')

    # Create residents with fixed street addresses
    r1 = Resident(username='law', password='pass123', name='Law', street='Main St')
    r2 = Resident(username='charlie', password='pass123', name='Charlie', street='Oak Ave')
    db.session.add_all([r1, r2])
    db.session.commit()

    # Create stop requests: residents request an existing drive to stop at their street
    try:
        # Use resident.street if no explicit street provided
        r1.create_stop_request(drive1)
        r2.create_stop_request(drive1)
        r1.create_stop_request(drive2)
        print("Stop requests created no problem")
    except Exception:
        # If any of the helper functions raise (e.g., drive not found), ignore to allow init to complete
        print ("Something went wrong. I dont fucking care, lets run the code anyway")
        pass

    print('database initialized with demo data')
