from flask import Blueprint, render_template, redirect, request, url_for, abort

import json, collections

from response_util import single_error as error
from eth_util import validate_id
from .models import Magic8Event, Magic8Scanner
from .constants import *

def make_result(block, scanner, tx, question, answer, status):
    return {"timestamp": block.timestamp, "scanner_id": scanner.id, "event_id": tx['hash'],
                    "data": json.dumps({"asker": tx['from'], "question": question,
                                         "answer": answer, 'status': status})}

# TODO -- compare transaction retrieval time to:
#   web3.eth.getBlockTransactionCount
#   web3.eth.getTransactionFromBlock
def scan_questions(db, web3, scanner, to_block):
    contract_hash = scanner.contract_hash.lower()
    results = []
    
    for block_num in range(scanner.next_block, to_block+1):
        block = web3.eth.getBlock(block_num)
        if not block:
            continue

        for tx_hash in block.transactions:
            receipt = web3.eth.getTransactionReceipt(tx_hash)
            tx = web3.eth.getTransaction(tx_hash)
            if not tx.input.startswith(scanner.function):
                print("{} {}".format(block_num, "Wrong function!"))
                continue
            print(tx.input[138:])
            if (not tx) or (len(tx.input) <= 138):
                print("{} {} {}".format(block_num, "This is not the transaction you're looking for.", len(tx.input)))
                continue
            question = bytearray.fromhex(tx.input[138:]).decode().strip('\x00')
            print(question)

            if not receipt:
                print("{} ".format(block_num)+"Transaction pending (this should never occur): "+tx_hash)
                results.append(make_result(block, scanner, tx, question, "", PENDING))
                continue
            if receipt['status'] != "0x1":
                print("{} Failed: {}".format(block_num, question))
                results.append(make_result(block, scanner, tx, question, "", FAILED))
            if receipt['to'] == contract_hash:
                if len(receipt['logs']) == 0:
                    continue
                data = receipt['logs'][0]['data']
                if len(data) < 130:
                    print("{} ".format(block_num)+"Invalid log length")
                    continue
                answer = bytearray.fromhex(data[130:]).decode().strip('\x00')
                results.append(make_result(block, scanner, tx, question, answer, SUCCESS))
                print("{} ".format(block_num)+"Question: {}\nanswer: {}".format(question, answer))
    scanner.next_block = to_block+1
    print("Scanned to block {}".format(scanner.next_block))
    return results

def run_question_scan(app):
    scanner = app.db.session.query(Magic8Scanner).filter_by(function=r"0x602bdec8").first()
    if not scanner:
        return False

    print("Scanning, id={}...".format(scanner.id))
    results = scan_questions(app.db, app.web3, scanner, app.web3.eth.blockNumber)

    for result in results:
        data = result['data']
        event = app.db.session.query(Magic8Event).filter_by(event_id=result['event_id']).first()
        if event:
            event.timestamp = result['timestamp']
            event.data = data
        else:
            app.db.session.add(Magic8Event(**result))

    app.db.session.commit()
    return True

def get_events(db):
    query = Magic8Event.query.order_by(Magic8Event.id.desc()).all()
    return [event.to_web() for event in query]

def make_magic8_blueprint(app):

    blueprint = Blueprint('magic8ball', __name__, static_folder='static',
                            template_folder='templates', static_url_path='/static')

    @blueprint.route("/")
    def magic8():
        print(url_for('magic8ball.static', filename='js/magic8.js'))
        run_question_scan(app)
        events = get_events(app.db)
        print(events)
        print(PODO_TEST_INFO)
        return render_template("magic8.html", events=json.dumps(events),
            podoTestInfo=json.dumps(PODO_TEST_INFO))
    
    
    @blueprint.route("/api/events/", methods=['POST'])
    def api_events():
        scanner_id = request.form.get("scanner_id")
        
        if scanner_id:
            scanner = Magic8Scanner.query.get(scanner_id)
            if scanner:
                currentBlock = app.web3.eth.blockNumber
                print("Unscanned blocks: "+(currentBlock - scanner.latest_block))
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
        run_question_scan(app)
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
