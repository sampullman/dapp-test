from flask import Blueprint, render_template, redirect, request, url_for, abort

import json

from response_util import single_error as error
from eth_util import validate_id

CONTRACT_ID = '0x16dF1321541Db03Fc2f1AA071ae8f73F1180b774'

def make_erc20_blueprint(app):

    blueprint = Blueprint('erc20', __name__, static_folder='static',
                            template_folder='templates', static_url_path='/erc20/static')

    @blueprint.route("/")
    def browser():
        return render_template("erc20.html")

    @blueprint.route("/api/balance/", methods=['POST'])
    def api_balance():
        account_id = validate_id(request.form.get("id"))
        if account_id.startswith('0x'):
            account_id = account_id[2:]
        balances_index = '1'
        if account_id:
            try:
                key_str = '0x{0:0>64}{1:0>64}'.format(account_id, balances_index)
                print(key_str)
                index = app.web3.sha3(hexstr=key_str)
                balance = int(app.web3.eth.getStorageAt(CONTRACT_ID, int(index, 16)), 16)

                return json.dumps({"id": account_id, "balance": balance})
            except ValueError as ve:
                print(ve)
                return error("Invalid account or contract address.")
            except Exception as e:
                print(e)
                return error("Unknown error accessing contract.")
        else:
            return error("Account id required.")

    @blueprint.route("/api/erc20/send/", methods=['POST'])
    def api_send():
        tx_data = validate_id(request.form.get("tx_data"))
        print(request.form.get("tx_data"))
        if tx_data:
            try:
                tx_id = app.web3.eth.sendRawTransaction(tx_data)
                return json.dumps({"tx_id": tx_id})
            except ValueError as e:
                print(e.args)
                return error('Error: {}'.format(e.args[0]['message']))
        else:
            return error("Malformed transaction, check private key.")

    return blueprint
