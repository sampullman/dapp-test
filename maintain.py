from application import app
from magic8ball.models import Magic8Scanner, Magic8Event
from magic8ball import run_question_scan
from magic8ball.constants import *

app.db.create_all()

contract_hash = PODO_TEST_INFO['contract_hash']

# Initialize Magic8Scanner table
if app.db.session.query(Magic8Scanner).filter_by(contract_hash=contract_hash).scalar() is None:
    print("Initializing "+PODO_TEST_INFO['name'])
    scanner = Magic8Scanner(**PODO_TEST_INFO)
    app.db.session.add(scanner)
    app.db.session.commit()

    run_question_scan(app)