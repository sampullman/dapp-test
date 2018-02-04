from flask import Blueprint, render_template, redirect, request, url_for, abort

import json, requests, binascii

from response_util import single_error as error
from eth_util import validate_id

CONTRACT_ID = '0x03F5B34f50a19cc97D64E22C74FCd192bE5Eb8b7'

def get_uint256(web3, contract_id, var_index):
    loc = '0x{0:0>64}'.format(var_index)
    return int(binascii.hexlify(web3.eth.getStorageAt(contract_id, loc)), 16)

def get_map_location(map_index, key):
    key_str = '0x{0:0>64}{1:0>64}'.format(map_index, key)
    loc = app.web3.sha3(hexstr=key_str)
    return int(loc, 16)

def get_map_value(web3, contract_id, map_index, key):
    location = get_map_location(map_index, key)
    balance = int(web3.eth.getStorageAt(contract_id, location), 16)

def make_erc20_blueprint(app):

    blueprint = Blueprint('erc20', __name__, static_folder='static',
                            template_folder='templates', static_url_path='/erc20/static')


    # Return value of 1 ETH in USD or None if not available
    @app.cache.cached(key_prefix='eth_value', timeout=180)
    def get_eth_value():
        url = "https://min-api.cryptocompare.com/data/price?fsym=ETH&tsyms=USD&extraParams=ccgtoken"
        try:
            response = requests.get(url=url, timeout=3)
            print(response)
            data = response.json().get('USD')
            if data:
                return int(data)
        except requests.exceptions.RequestException as e:
            app.logger.info("Error getting eth "+repr(e))
        return None

    @blueprint.route("/")
    def browser():
        token_price = get_uint256(app.web3, CONTRACT_ID, '2')
        return render_template("erc20.html", eth_value=get_eth_value(), token_price=token_price)

    @blueprint.route("/getting_started/")
    def buying_tokens():
        return render_template("tutorial.html")

    @blueprint.route("/api/balance/", methods=['POST'])
    def api_balance():
        account_id = validate_id(request.form.get("id"))
        if account_id.startswith('0x'):
            account_id = account_id[2:]
        balances_index = '1'
        if account_id:
            try:
                balance = get_map_value(app.web3, CONTRACT_ID, balances_index, account_id)

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
