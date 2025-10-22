
from App.database import db
from App.models.user import User
from datetime import datetime

class Driver(User):
    __tablename__ = 'driver'
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    status = db.Column(db.String(50), nullable=True)

    # one-to-many: Driver -> Drive
    schedule = db.relationship('Drive', back_populates='driver', cascade='all, delete-orphan')

    __mapper_args__ = {
        'polymorphic_identity': 'driver',
    }

    def __init__(self, username, password, status=None):
        super().__init__(username, password)
        self.status = status

    def add_drive(self, when=None, current_location=None):
        """Create a Drive for this driver and persist it."""
        when = when or datetime.utcnow()
        drive = Drive(datetime=when, current_location=current_location, driver=self)
        db.session.add(drive)
        db.session.commit()
        return drive

    def __repr__(self):
        return f"<Driver id={self.id} username={self.username} status={self.status}>"

class Drive(db.Model):
    __tablename__ = 'drive'
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    current_location = db.Column(db.String(120), nullable=True)

    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'))
    driver = db.relationship('Driver', back_populates='schedule')

    # one-to-many: Drive -> StopRequest
    stops = db.relationship('StopRequest', back_populates='drive', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Drive id={self.id} datetime={self.datetime} driver_id={self.driver_id} current_location={self.current_location}>"
