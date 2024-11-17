from . import db
from sqlalchemy.dialects.postgresql import UUID

class ResearchOutputAuthor(db.Model):
    __tablename__ = 'research_output_authors'
    research_id = db.Column(db.String(15), db.ForeignKey('research_outputs.research_id'), primary_key=True)
    author_id = db.Column(UUID(as_uuid=True), db.ForeignKey('account.user_id'), primary_key=True)
    author_order = db.Column(db.Integer)
