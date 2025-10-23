from App.database import db
from datetime import datetime

class StopRequest(db.Model):
    __tablename__ = 'stop_request'
    id = db.Column(db.Integer, primary_key=True)

    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    drive = db.relationship('Drive', back_populates='stops')

    # simplified: store street name directly rather than a separate Street model
    street_name = db.Column(db.String(120), nullable=True)

    requestee_id = db.Column(db.Integer, db.ForeignKey('resident.id'))
    requestee = db.relationship('Resident', back_populates='stop_requests')

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __init__(self, drive, street_name, requestee):
        self.drive = drive
        self.street_name = street_name
        self.requestee = requestee

    def __repr__(self):
        return f"<StopRequest id={self.id} drive_id={self.drive_id} street_name={self.street_name} requestee_id={self.requestee_id}>"