from flask import Blueprint, render_template, redirect, request, url_for, abort

import json, collections

from response_util import single_error as error
from eth_util import validate_id, safe_blocknumber
from .models import Magic8Event, Magic8Scanner
from .constants import *
from .scan import scan_questions, scan_questions2, scan_questions3

SCAN_RAN = 0
SCAN_ERROR = 1
SCAN_UNNECESSARY = 2

def run_question_scan(app):
    scanner = app.db.session.query(Magic8Scanner).filter_by(function=r"0x602bdec8").first()
    blockNumber = safe_blocknumber(app.web3)
    if not scanner or (blockNumber is None):
        return SCAN_ERROR
    elif scanner.next_block > blockNumber:
        return SCAN_UNNECESSARY

    print("Scanning, id={}...".format(scanner.id))
    results = scan_questions(app.db, app.web3, scanner, blockNumber)

    for result in results:
        data = result['data']
        event = app.db.session.query(Magic8Event).filter_by(event_id=result['event_id']).first()
        if event:
            event.timestamp = result['timestamp']
            event.data = data
        else:
            app.db.session.add(Magic8Event(**result))

    app.db.session.commit()
    return SCAN_RAN

def get_events(db):
    query = Magic8Event.query.order_by(Magic8Event.id.desc()).all()
    return [event.to_web() for event in query]

def make_magic8_blueprint(app):

    blueprint = Blueprint('magic8ball', __name__, static_folder='static',
                            template_folder='templates', static_url_path='/static')

    @blueprint.route("/")
    def magic8():
        print(url_for('magic8ball.static', filename='js/magic8.js'))
        scan_result = run_question_scan(app)
        events = get_events(app.db)
        print(events)
        print(PODO_TEST_INFO)
        return render_template("magic8.html", events=json.dumps(events), scan_result=scan_result,
            podoTestInfo=json.dumps(PODO_TEST_INFO))
    
    
    @blueprint.route("/api/events/", methods=['POST'])
    def api_events():
        scanner_id = request.form.get("scanner_id")
        
        if scanner_id:
            scanner = Magic8Scanner.query.get(scanner_id)
            if scanner:
                currentBlock = safe_blocknumber(app.web3)
                print("Unscanned blocks: "+(currentBlock - scanner.latest_block))
                if currentBlock is None:
                    return error("Can't connect to the Ethereum node.")
                if scanner.latest_block == currentBlock:
                    events = app.db.session.query(Magic8Event).filter_by(scanner_id=scanner_id).all()
                else:
                    events = scan_questions(app.db, app.web3, scanner.latest_block, currentBlock)
                return json.dumps([e.to_web() for e in events])
            else:
                return error("Invalid scanner id.")
        else:
            return error("Missing scanner id.")

    @blueprint.route("/api/question/", methods=['POST'])
    def api_question():
        question = request.form.get("question")
        print(request.form.get("question"))
        if question:
            return json.dumps({"answer": "Done"})
        else:
            return error("Error - no question detected.")

    @blueprint.route("/api/answer/", methods=['POST'])
    def api_answer():
        scan_result = run_question_scan(app)
        tx_hash = request.form.get("tx_hash")

        if tx_hash:
            entry = app.db.session.query(Magic8Event).filter_by(event_id=tx_hash).order_by(Magic8Event.id.desc()).first()
            if entry:
                events = get_events(app.db)
                return json.dumps({"pending": False, "result": entry.to_web(), "events": events})
            else:
                return json.dumps({"pending": True})
        else:
            return error("Invalid transaction.")
    
    return blueprint
