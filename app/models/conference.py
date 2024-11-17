from . import db

class Conference(db.Model):
    __tablename__ = 'conference'
    conference_id = db.Column(db.String(15), primary_key=True)
    conference_title = db.Column(db.String(100))
    conference_venue = db.Column(db.String(100))
    conference_date = db.Column(db.Date)