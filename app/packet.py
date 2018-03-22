import json
from flask import jsonify

def _packet(t, v, c=200):
    response = json.dumps({
        'type': t,
        'value': v,
    }) + '\n'
    return response

def Status(data):
    return _packet('status', data)

def Progress(data):
    return _packet('progress', data)

def Keepalive():
    return '{}\n'

def Cell(data):
    return _packet('cell', data)

def Notebook(data):
    return _packet('notebook', data)

def Error(data):
    return _packet('error', data)

def Suggest(suggestions):
    response = jsonify(suggestions)
    response.status_code = 200
    return response
