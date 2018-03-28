import re
import nbformat as nbf
from jinja2 import Environment
from flask import current_app

cell_match = re.compile(r'^#?%%nbtemplate(.*?\n)(.+)$', re.MULTILINE | re.DOTALL)
template_match = re.compile(r'\{[\{%](.+?)[%\}]\}', re.MULTILINE | re.DOTALL)
field_match = re.compile(r'([A-Za-z_]+\(([\'"].+?[\'"]|.)+?\))', re.MULTILINE | re.DOTALL)

def render_notebook(nb, context):
    env = Environment(extensions=['jinja2.ext.do'])
    env.filters['re_match'] = lambda target, expr: re.match(expr, str(target)).groups()
    env.globals = context

    nb.cells = [
        cell
        for cell in [
            render_cell(
                cell,
                env,
            )
            for cell in nb.cells
        ]
        if cell is not None
    ]
    return nb

def render_cell(cell, env):
    if cell.cell_type == 'code':
        cell.outputs = []
        cell['execution_count'] = None

    cell_m = cell_match.match(cell.source)
    if cell_m:
        line = cell_m.group(1).strip()
        cell_source = cell_m.group(2).strip()

        if line == 'init':
            return None

        template = env.from_string(cell_source)
        rendered = template.render().strip()

        for k, v in template.module.__dict__.items():
            if not k.startswith('_'):
                env.globals[k] = v

        if line == 'markdown':
            cell = nbf.v4.new_markdown_cell(rendered)
        elif line == 'hide' or rendered == '':
            cell = None
        else:
            cell = nbf.v4.new_code_cell(rendered)
    return cell

def parse_fields(cell, context):
    cell_m = cell_match.match(cell)
    if cell_m:
        cell_source = cell_m.group(2)
        for template_m in template_match.finditer(cell_source):
            for field_m in field_match.finditer(template_m.group(1)):
                try:
                    yield eval(field_m.group(1), context)
                except:
                    pass
