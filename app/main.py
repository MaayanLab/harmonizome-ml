#!/usr/bin/env python3

import os
from flask import request, abort, send_from_directory, render_template, jsonify
from werkzeug.serving import WSGIRequestHandler
from . import app
from .search import perform_search
from .runtime import process_notebook
from .util import app_dir, PREFIX, PORT, DEBUG, globalContext
import datetime
@app.route(PREFIX + "/", methods=['GET', 'POST'])
def api():
    try:
        if request.method == 'GET':
            field = request.args.get('field')
            query = request.args.get('q')
            if field and query:
                return perform_search(field, query)
        elif request.method == 'POST':
            return process_notebook(request.get_json())
        return render_template('primary.html', **globalContext)
    except Exception as e:
        print('Error:', e)
        return str(e)
        # abort(404)

@app.route(PREFIX + "/test", methods=['GET'])
def test():
    return render_template('test.html', **globalContext)

@app.route(PREFIX + "/autocomplete", methods=['GET'])
def autocomplete():
    return jsonify([
        'a',
        'b',
        'c',
    ])

@app.route(PREFIX + "/suggest", methods=['GET'])
def suggest():
    return jsonify({
        'training-datasets': [{'id': 'a', 'text': 'a'}],
        'label-datasets': [{'id': 'b', 'text': 'b'}, {'id': 'c', 'text': 'c'}],
    })

def main():
    # Only for debugging while developing

    # Route static path
    @app.route(PREFIX + '/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)

    # Route node_modules path
    @app.route(PREFIX + '/node_modules/<path:path>')
    def send_node_modules(path):
        return send_from_directory('../node_modules', path)

    # Setup debugging server
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(host='0.0.0.0', debug=DEBUG, port=PORT, threaded=True)
