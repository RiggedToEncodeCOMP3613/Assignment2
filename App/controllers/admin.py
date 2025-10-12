from App.database import db
from App.models import User, Driver, Drive, Resident, StopRequest


def list_all_data():
    """Return a dict containing all rows for each model in JSON-serializable form."""
    data = {}

    # Users - use existing get_json if available
    users = db.session.scalars(db.select(User)).all()
    data['users'] = [u.get_json() if hasattr(u, 'get_json') else {'id': u.id, 'username': getattr(u, 'username', None)} for u in users]

    # Drivers
    drivers = db.session.scalars(db.select(Driver)).all()
    data['drivers'] = [{'id': d.id, 'status': d.status} for d in drivers]

    # Drives
    drives = db.session.scalars(db.select(Drive)).all()
    def drive_to_dict(dr):
        return {
            'id': dr.id,
            'datetime': dr.datetime.isoformat() if getattr(dr, 'datetime', None) is not None else None,
            'driver_id': dr.driver_id,
            'stops': [s.id for s in getattr(dr, 'stops', [])]
        }
    data['drives'] = [drive_to_dict(dr) for dr in drives]

    # Residents
    residents = db.session.scalars(db.select(Resident)).all()
    data['residents'] = [{'id': r.id, 'name': r.name, 'street': r.street} for r in residents]

    # StopRequests (now reference street_name)
    srs = db.session.scalars(db.select(StopRequest)).all()
    data['stop_requests'] = [{'id': s.id, 'drive_id': s.drive_id, 'street_name': s.street_name, 'requestee_id': s.requestee_id,
                               'created_at': s.created_at.isoformat() if getattr(s, 'created_at', None) else None} for s in srs]

    return data


def print_all_data():
    """Pretty-print all data to stdout for CLI usage."""
    data = list_all_data()
    print('\n=== USERS ===')
    for u in data['users']:
        print(u)
    print('\n=== DRIVERS ===')
    for d in data['drivers']:
        print(d)
    print('\n=== DRIVES ===')
    for dr in data['drives']:
        print(dr)
    print('\n=== RESIDENTS ===')
    for r in data['residents']:
        print(r)
    print('\n=== STOP REQUESTS ===')
    for s in data['stop_requests']:
        print(s)

    return data