from App.database import db
from App.models.stoprequest import StopRequest

class Resident(db.Model):
    __tablename__ = 'resident'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    # resident has a fixed street/address (string)
    street = db.Column(db.String(120), nullable=True)
    stop_requests = db.relationship('StopRequest', back_populates='requestee', cascade='all, delete-orphan')

    def view_inbox(self, street=None):
        # If no filter provided, return all stop requests for this resident
        if street is None:
            return list(self.stop_requests)
        # Compare by street name string
        return [sr for sr in self.stop_requests if sr.street_name == str(street)]

    def create_stop_request(self, drive, street=None):
        """Create a StopRequest for this resident for the given drive.
        If street is provided it is used, otherwise resident.street is used.
        drive may be a Drive instance or an integer id."""
        from App.database import db as _db
        from App.models.driver import Drive as DriveModel

        # resolve street_name from parameter or resident attribute
        street_name = str(street) if street is not None else self.street

        # resolve drive
        if isinstance(drive, DriveModel):
            drive_obj = drive
        else:
            try:
                drive_obj = _db.session.get(DriveModel, int(drive))
            except Exception:
                drive_obj = None

        if not drive_obj:
            raise ValueError('Drive not found')

        sr = StopRequest(drive=drive_obj, street_name=street_name, requestee=self)
        _db.session.add(sr)
        _db.session.commit()
        return sr

    def view_driver_status(self, driver):
        from App.models.driver import Driver
        if isinstance(driver, Driver):
            d = driver
        else:
            d = db.session.get(Driver, int(driver))
        return d.status if d else None

    def __repr__(self):
        return f"<Resident id={self.id} name={self.name}>"