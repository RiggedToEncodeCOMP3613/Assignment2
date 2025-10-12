from App.models import Resident
from App.database import db

def create_resident(name=None, street=None):
    r = Resident(name=name, street=street)
    db.session.add(r)
    db.session.commit()
    return r

def get_resident(id):
    return db.session.get(Resident, id)

# Updated: accept drive_id to associate the StopRequest with an existing Drive
def create_stop_request(resident_id, drive_id, street):
    resident = get_resident(resident_id)
    if not resident:
        return None
    try:
        return resident.create_stop_request(drive_id, street)
    except Exception:
        # drive not found or other error
        return None

def get_resident_inbox(resident_id, street=None):
    resident = get_resident(resident_id)
    if not resident:
        return []
    return resident.view_inbox(street)