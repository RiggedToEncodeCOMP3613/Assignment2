from App.database import db
from App.models import User, Driver, Drive, Resident, StopRequest

# Optional pretty printing with rich if available
try:
    from rich.console import Console
    from rich.table import Table
    _RICH_AVAILABLE = True
    _CONSOLE = Console()
except Exception:
    _RICH_AVAILABLE = False


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
    # If rich is available, render nice tables. Otherwise fall back to simple prints.
    def _render_table(title, rows):
        if not rows:
            if _RICH_AVAILABLE:
                _CONSOLE.print(f"\n[bold]{title}[/bold] (empty)")
            else:
                print(f"\n=== {title} === (empty)")
            return

        # If rows are dict-like, take keys as columns. For simple lists, show single column.
        if _RICH_AVAILABLE:
            # normalize rows to list of dicts
            if isinstance(rows, (list, tuple)) and rows and isinstance(rows[0], dict):
                columns = []
                for r in rows:
                    for k in r.keys():
                        if k not in columns:
                            columns.append(k)
            else:
                # fallback single column
                columns = ["value"]

            table = Table(title=title)
            for col in columns:
                table.add_column(col, overflow="fold")

            for r in rows:
                if isinstance(r, dict):
                    row = [str(r.get(c, "")) for c in columns]
                else:
                    row = [str(r)]
                table.add_row(*row)

            _CONSOLE.print(table)
        else:
            print(f"\n=== {title} ===")
            for r in rows:
                print(r)

    _render_table('USERS', data.get('users', []))
    _render_table('DRIVERS', data.get('drivers', []))
    _render_table('DRIVES', data.get('drives', []))
    _render_table('RESIDENTS', data.get('residents', []))
    _render_table('STOP REQUESTS', data.get('stop_requests', []))

    return data