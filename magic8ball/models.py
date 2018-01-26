from app_objects import db
from sqlalchemy.sql.expression import literal
import json

from .constants import *

class Magic8Scanner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    first_block = db.Column(db.Integer, default=0, nullable=False)
    next_block = db.Column(db.Integer, default=0, nullable=False)
    function = db.Column(db.String(8), nullable=False)
    contract_hash = db.Column(db.String(42), nullable=False)

    def to_web(self):
        return {"id": self.id, "first_block": self.start_block,
                "next_block": self.latest_block, "contract_hash": self.block_hash}

# Data formats:
# Question: {"asker": <account str>, "question": <str>, "answer": <str>, "status": <int>}
class Magic8Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.String(), nullable=False)
    timestamp = db.Column(db.Integer)
    event_type = db.Column(db.Integer, default=0, server_default=literal(0), nullable=False)
    data = db.Column(db.Text, nullable=False)

    scanner_id = db.Column(db.Integer, db.ForeignKey('magic8_scanner.id'), nullable=False)
    scanner = db.relationship('Magic8Scanner', backref=db.backref('events', lazy=True))

    def to_web(self):
        data = json.loads(self.data)
        print(data['answer']+"end")
        data['status'] = STATUS_IMAGES[data['status']]
        return {"id": self.id, "timestamp": self.timestamp,
                "event_type": self.event_type, "data": data}

