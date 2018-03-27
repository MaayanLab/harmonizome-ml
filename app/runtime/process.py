import traceback
import sys
import time
from flask import Response, stream_with_context, current_app
from packet import *
from util import data_dir
from .render import render_ipynb
from .convert import ipynb_export_html, ipynb_export_nb
from .execute import CustomExecutePreprocessor, CellExecutionError
from threading import Thread
from queue import Queue

def cellIsCode(cell):
    return cell.get('cell_type') == 'code'

def cellHasError(cell):
    for output in cell['outputs']:
        if output['output_type'] == 'error':
            return True
    return False

def keepalive(thread_yield, thread_stopper, timeout):
    while not thread_stopper():
        time.sleep(timeout)
        thread_yield(Keepalive())

def execute_notebook(thread_yield, thread_stopper, app, args):
    try:
        with app.app_context():
            thread_yield(Status('Constructing notebook...'))
            nb = render_ipynb(args)
            thread_yield(Notebook(ipynb_export_html(nb)))

            thread_yield(Status('Executing notebook...'))
            ep = CustomExecutePreprocessor(allow_errors=True, timeout=None, kernel_name='python3')
            resources = {'metadata': {'path': data_dir}}
            index = 0
            code_cell_index = 0
            n_cells = len(nb.cells)
            thread_yield(Progress(index))
            for cell, _ in ep.preprocess(nb, resources):
                if thread_stopper():
                    raise Exception('Thread stopped')
                thread_yield(Cell(cell))
                if cellIsCode(cell):
                    code_cell_index += 1
                    if cellHasError(cell):
                        raise Exception('Cell execution error on cell %d' % (code_cell_index))
                index += 1
                if index < n_cells:
                    thread_yield(Progress(index))
                else:
                    thread_yield(Status('Success'))
                    thread_yield(Notebook(ipynb_export_nb(nb)))
    except Exception as e:
        traceback.print_exc(file=open('error.log', 'a'))
        thread_yield(Error(str(e)))
    finally:
        thread_yield(None)

def process_notebook(args):
    # By yielding a structured JSON with the Response stream_with_context
    #  we can send progress to a javascript handler on the webpage.
    def generate_notebook():
        # Prepare thread communications
        thread_queue = Queue()
        thread_stop = False
        thread_yield = lambda val: thread_queue.put(val)
        thread_stopper = lambda: thread_stop

        try:
            # Start threads
            threads = [
                Thread(target=execute_notebook, args=(thread_yield, thread_stopper, current_app._get_current_object(), args)),
                Thread(target=keepalive, args=(thread_yield, thread_stopper, 10)),
            ]
            list(map(Thread.start, threads))

            # Process thread message queue
            current_packet = thread_queue.get()
            while current_packet != None:
                yield current_packet
                current_packet = thread_queue.get()

            # Stop threads
            thread_stopper = True
            list(map(Thread.join, threads))
        except Exception as e:
            thread_stop = True
            traceback.print_exc(file=sys.stdout)
            yield Error(str(e))
    return Response(stream_with_context(generate_notebook()))
