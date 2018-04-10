#!/usr/bin/env python

import os
import nbformat
from flask import render_template
from . import app
from .model import build_form_fields
from .runtime import ipynb_import_from_file
from .template.nbtemplate_parse import parse_fields
from .util import app_dir, globalContext

@app.template_filter('filter')
def reverse_filter(arr, attr, val):
  def maybe_eval(v):
    if callable(v):
      return v()
    return v
  return [v
          for v in  arr
          if maybe_eval(getattr(v, attr)) == val]

def main():
  with app.test_request_context('/'):
    for _, _, files in os.walk(app_dir + '/templates/ipynb/'):
      for file in files:
        file, ext = os.path.splitext(file)
        if ext != '.ipynb':
          continue

        print('Building %s...' % (file))

        nb = ipynb_import_from_file(
          app_dir + '/templates/ipynb/%s.ipynb' % (file)
        )

        context = dict(
          filename=file,
          **globalContext,
          **build_form_fields(),
        )

        fields = [field
                  for cell in nb.cells
                  for field in parse_fields(
                    cell['source'],
                    context,
                  )]

        form_out = open(app_dir + '/templates/%s.html' % (file), 'w')

        try:
          if os.path.isfile(app_dir + '/templates/ipynb/%s.html' % (file)):
            # Custom template
            print(
              render_template('ipynb/%s.html' % (file),
                **context,
                fields=fields,
              ),
              file=form_out,
            )
          else:
            # General template
            print(
              render_template('layout/ipynb.j2',
                **context,
                fields=fields,
              ),
              file=form_out,
            )
        except Exception as e:
          print(e)
        finally:
          form_out.close()

      break
