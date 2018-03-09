import traceback
import sys
from flask import Response, stream_with_context
from packet import *
from util import data_dir
from .render import render_ipynb
from .convert import ipynb_export_html, ipynb_export_nb
from .execute import CustomExecutePreprocessor, CellExecutionError

def cellIsCode(cell):
    return cell.get('cell_type') == 'code'

def cellHasError(cell):
    for output in cell['outputs']:
        if output['output_type'] == 'error':
            return True
    return False

def process_notebook(args):
    # By yielding a structured JSON with the Response stream_with_context
    #  we can send progress to a javascript handler on the webpage.
    def generate_notebook():
        try:
            yield Status('Constructing notebook...')
            nb = render_ipynb(args)
            yield Notebook(ipynb_export_html(nb)) # could also just pass nb here and convert it client side

            yield Status('Executing notebook...')
            ep = CustomExecutePreprocessor(allow_errors=True, timeout=6000, kernel_name='python3')
            resources = {'metadata': {'path': data_dir}}
            index = 0
            code_cell_index = 0
            n_cells = len(nb.cells)
            yield Progress(index)
            for cell, _ in ep.preprocess(nb, resources):
                yield Cell(cell)
                if cellIsCode(cell):
                    code_cell_index += 1
                    if cellHasError(cell):
                        raise Exception('Cell execution error on cell %d' % (code_cell_index))
                index += 1
                if index < n_cells:
                    yield Progress(index)
                else:
                    yield Status('Success')
                    yield Notebook(ipynb_export_nb(nb))
        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            yield Error(str(e))
    return Response(stream_with_context(generate_notebook()))
