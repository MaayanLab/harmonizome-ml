import os
import re
from flask import render_template_string
from model import build_safe_value
from .convert import ipynb_import_from_file, ipynb_export_nb
from util import globalContext
from template.nbtemplate_parse import render_cell

filename_constraint = re.compile(r'^[A-Za-z-_]+$')
field_match = re.compile(r'\{\{(.+?)\}\}', re.MULTILINE | re.DOTALL)

def render_ipynb(context):
    filename = context.get('filename')
    if filename is None or not filename_constraint.match(filename):
        raise Exception("Filename constraint not satisfied")

    context.update(
        **globalContext,
    )
    context.update(
        **build_safe_value(context),
    )

    nb = ipynb_import_from_file(os.path.join('templates', 'ipynb', filename + '.ipynb'))

    for index, cell in enumerate(nb.cells):
        nb.cells[index].source = render_cell(
            cell['source'],
            context,
        )
    nb.cells = [cell for cell in nb.cells if cell.source]
    return nb
