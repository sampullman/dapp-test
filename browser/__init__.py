from flask import Blueprint, render_template, redirect, request, url_for, abort

import json

def make_browser_blueprint(app):

    blueprint = Blueprint('browser', __name__, static_folder='static',
                            template_folder='templates', static_url_path='/browser/static')

    @blueprint.route("/")
    def browser():
        #app.logger.info("Load Browser")
        return render_template("browser.html")

    @blueprint.route("/api/account/", methods=['POST'])
    def api_account():
        account_id = validate_id(request.form.get("id"))
        if account_id:
            try:
                balance = app.web3.eth.getBalance(account_id)
                tx_count = app.web3.eth.getTransactionCount(account_id)
                return json.dumps({"id": account_id, "balance": balance, "tx_count": tx_count})
            except ValueError as ve:
                return json.dumps({"errors": ["Invalid account address."]})
            except Exception as e:
                return json.dumps({"errors": ["Unknown error accessing account."]})
        else:
            return json.dumps({"errors": ["Account id required."]})

    @blueprint.route("/api/transaction/", methods=['POST'])
    def api_transaction():
        tx_id = validate_id(request.form.get("id"))
        if tx_id:
            try:
                tx = dict(app.web3.eth.getTransaction(tx_id))
                print(dir(tx))
                tx_receipt = dict(app.web3.eth.getTransactionReceipt(tx_id))
                if tx_receipt:
                    tx['txReceipt'] = True
                    tx['gasUsed'] = tx_receipt['gasUsed']
                    tx['cumulativeGasUsed'] = tx_receipt['cumulativeGasUsed']
                return json.dumps({**tx, **tx_receipt})
            except ValueError as ve:
                return json.dumps({"errors": ["Invalid transaction address."]})
            except Exception as e:
                print("EXCEPTION: "+str(e))
                return json.dumps({"errors": ["Unknown error."]})
        else:
            return json.dumps({"errors": ["Transaction id required."]})

    return blueprint

def validate_id(hash):
    if hash:
        if not hash.startswith("0x"):
            hash = "0x{}".format(hash)
        return hash
    else:
        return False
