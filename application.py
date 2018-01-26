from web3 import Web3, IPCProvider
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from os.path import abspath, dirname
from app_objects import create_db
import os

basedir = abspath(dirname(__file__))

debug = (os.environ.get('FLASK_DEBUG', '0') == '1')
stage = (os.environ.get('FLASK_STAGE', '0') == '1')

app = Flask(__name__)
app.web3 = Web3(IPCProvider("./chain/geth.ipc"))
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'development_key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if debug or stage:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.sqlite3'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.sqlite3'

app.db = create_db(app)

from browser import make_browser_blueprint
from erc20 import make_erc20_blueprint
from magic8ball import make_magic8_blueprint

csrf = CSRFProtect(app)

app.register_blueprint(make_browser_blueprint(app))
app.register_blueprint(make_erc20_blueprint(app), url_prefix="/erc20")
app.register_blueprint(make_magic8_blueprint(app), url_prefix="/magic8ball")

application = app
