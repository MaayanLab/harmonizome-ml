import os
import re
from flask import render_template_string
from .convert import ipynb_import_from_file, ipynb_export_nb
from ..model import build_fields
from ..util import globalContext, app_dir
from ..template.nbtemplate_parse import render_notebook

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
        **build_fields(context),
    )

    nb = ipynb_import_from_file(os.path.join(app_dir, 'templates', 'ipynb', filename + '.ipynb'))
    return render_notebook(nb, context)
