import re
from flask import render_template_string

cell_match = re.compile(r'^#?%%nbtemplate(.*?\n)(.+)$', re.MULTILINE | re.DOTALL)
field_match = re.compile(r'\{\{(.+?)\}\}', re.MULTILINE | re.DOTALL)

def render_cell(cell, context):
    cell_m = cell_match.match(cell)
    if cell_m:
        line = cell_m.group(1).strip()
        cell = cell_m.group(2)
        if line in ['hide', 'init']:
            return ''
        return render_template_string(
            cell, **context,
        )
    else:
        return cell


def parse_fields(cell, context):
    cell_m = cell_match.match(cell)
    if cell_m:
        cell_source = cell_m.group(2)
        for field_m in field_match.finditer(cell_source):
            try:
                yield eval(field_m.group(1), context)
            except:
                pass
