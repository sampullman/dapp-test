import json

def single_error(error):
    return json.dumps({"errors": [error]})