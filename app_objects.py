from flask_sqlalchemy import SQLAlchemy

db = None

def create_db(app):
    global db
    db = SQLAlchemy(app)
    return db