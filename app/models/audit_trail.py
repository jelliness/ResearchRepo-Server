from . import db
from sqlalchemy.dialects.postgresql import UUID
import datetime

class AuditTrail(db.Model):
    __tablename__ = 'audit_trail'
    audit_id = db.Column(db.String(16), primary_key=True)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.user_id'))
    table_name = db.Column(db.String(50))
    record_id = db.Column(db.String(16))
    operation = db.Column(db.String(50))
    change_datetime = db.Column(db.TIMESTAMP)
    action_desc = db.Column(db.String(100))



