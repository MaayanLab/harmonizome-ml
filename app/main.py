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
from itertools import count
n = iter(count())
test_data = {
    'training-datasets': [
        {
            'id': next(n),
            'text': 'training-datasets-1',
            'alias': ['tag-a',],
        },
        {
            'id': next(n),
            'text': 'training-datasets-2',
            'alias': ['tag-b',],
        },
    ],
    'label-datasets': [
        {
            'id': next(n),
            'text': 'label-datasets-1',
            'alias': ['tag-a',],
        },
        {
            'id': next(n),
            'text': 'label-datasets-2',
            'alias': ['tag-b',],
        },
    ],
    'dimensionality-reduction': [
        {
            'id': next(n),
            'text': 'T-SNE',
            'alias': ['dimensionality', 'reduction', 'tsne',],
        },
        {
            'id': next(n),
            'text': 'PCA',
            'alias': ['dimensionality', 'reduction',],
        },
    ],
    'target': [
        {
            'id': next(n),
            'text': 'target-1',
            'alias': ['tag-a',],
        },
        {
            'id': next(n),
            'text': 'target-2',
            'alias': ['tag-b',],
        },
    ],
    'understand-data': [
        {
            'id': next(n),
            'text': 'Visualize Problem Space',
            'alias': ['visualize', 'pca', 'dimensionality', 'reduction',],
        },
    ],
    'machine-learning': [
        {
            'id': next(n),
            'text': 'Random Forest',
            'alias': ['random', 'forest', 'tree',],
        },
        {
            'id': next(n),
            'text': 'Gradient Descent',
            'alias': ['sgd', 'gradient',],
        },
    ],
    'validation': [
        {
            'id': next(n),
            'text': 'KFold',
            'alias': ['cross', 'validation',],
        },
        {
            'id': next(n),
            'text': 'Randomized Hyperparameter Search',
            'alias': ['parameter', 'search', 'hyperparameter',],
        },
    ],
    'understand-model': [
        {
            'id': next(n),
            'text': 'Tabular Predictions',
            'alias': ['predictions',],
        },
        {
            'id': next(n),
            'text': 'ROC Curve',
            'alias': ['performance',],
        },
    ],
}

def like(str1, str2, strict=False):
    return any([
        str1.lower().find(str2.lower()) != -1,
        (str2.lower().find(str1.lower()) != -1) if strict else False,
    ])

@app.route(PREFIX + "/test", methods=['GET'])
def test():
    return render_template('test.html', **globalContext)

@app.route(PREFIX + "/autocomplete", methods=['GET'])
def autocomplete():
    return jsonify([
        element['text']
        for elements in test_data.values()
        for element in elements
        if any([
            like(element['text'], request.args.get('q')),
            *[like(tag, request.args.get('q'))
              for tag in element['alias']],
        ])
    ])

@app.route(PREFIX + "/suggest", methods=['GET'])
def suggest():
    return jsonify({
        category: [
            element
            for element in elements
            if like(request.args.get('q'), element['text'], strict=True)
        ]
        for category, elements in test_data.items()
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
