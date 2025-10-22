
from App.database import db
from App.models.user import User
from App.models.stoprequest import StopRequest

class Resident(User):
    __tablename__ = 'resident'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    name = db.Column(db.String(80), nullable=True)
    street = db.Column(db.String(120), nullable=True)
    stop_requests = db.relationship('StopRequest', back_populates='requestee', cascade='all, delete-orphan')

    __mapper_args__ = {
        'polymorphic_identity': 'resident',
    }

    def __init__(self, username, password, name=None, street=None):
        super().__init__(username, password)
        self.name = name
        self.street = street

    def view_inbox(self, street=None):
        if street is None:
            return list(self.stop_requests)
        return [sr for sr in self.stop_requests if sr.street_name == str(street)]

    def create_stop_request(self, drive, street=None):
        from App.database import db as _db
        from App.models.driver import Drive as DriveModel
        street_name = str(street) if street is not None else self.street
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
        return f"<Resident id={self.id} username={self.username} name={self.name}>"