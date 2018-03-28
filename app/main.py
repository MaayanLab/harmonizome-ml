#!/usr/bin/env python3

import os
from flask import Flask, request, abort, send_from_directory, render_template, jsonify
from search import perform_search
from runtime import process_notebook
from util import app_dir, PREFIX, PORT, DEBUG, globalContext
from werkzeug.serving import WSGIRequestHandler

app = Flask(__name__, static_url_path=PREFIX)
app.jinja_options = dict(
    app.jinja_options,
    extensions=['jinja2.ext.do'],
    trim_blocks=True,
    lstrip_blocks=True,
)

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

if __name__ == "__main__":
    # Only for debugging while developing

    # Route static path
    @app.route(PREFIX + '/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)

    # Setup debugging server
    WSGIRequestHandler.protocol_version = "HTTP/1.1"
    app.run(host='0.0.0.0', debug=DEBUG, port=PORT, threaded=True)
