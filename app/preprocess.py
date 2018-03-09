#!/usr/bin/env python

import os
import re
import nbformat
from model import build_form_fields
from runtime import ipynb_import_from_file
from flask import Flask, render_template_string
from jinja2 import meta, Template
from util import globalContext, app_dir

app = Flask(__name__, static_url_path='')

# TODO: ensue this is aware of escape rules
field_match = re.compile(r'\{\{(.+?)\}\}', re.MULTILINE | re.DOTALL)

with app.test_request_context('/'):
    for _, _, files in os.walk(app_dir + '/templates/ipynb/'):
        for file in files:
            # Though we don't use this, we can validate the notebook
            file, ext = os.path.splitext(file)
            if ext != '.ipynb':
                continue

            print('Building %s...' % (file))
            nb = ipynb_import_from_file(app_dir + '/templates/ipynb/%s.ipynb' % (file))
            form_out = open(app_dir + '/templates/%s.html' % (file), 'w')

            if os.path.isfile(app_dir + '/templates/ipynb/%s.html' % (file)):
                # Use pre-build form
                source = open(app_dir + '/templates/ipynb/%s.html' % (file), 'r').read()
                print(
                    render_template_string(
                        field_match.sub(r'{{ \1|safe }}', source),
                        **build_form_fields(),
                        **globalContext,
                    ),
                    file=form_out,
                )
            else:
                # Automatically build form
                for cell in nb.cells:
                    for field in field_match.finditer(cell.source):
                        f = field.group(1)
                        try:
                            print(Template('{{ %s|safe }}' % (f)).render(**build_form_fields(), **globalContext), file=form_out)
                        except:
                            pass
            form_out.close()
        break
