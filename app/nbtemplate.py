'''
IPython magic for making templating easy~. This basically
 just allows our jinja-type language to be executed in place
 injecting the defaults into the environment so we can easily
 debug the notebook at the same time as building the template.

The same call structure is used during preprocess and at runtime
 but performing different tasks--this way setting up a notebook is
 as simple as running it with different nbtemplate's being provided
 for import.

Usage (put the following in the first cell):

#%%nbtemplate init
import nbtemplate
nbtemplate.init(lambda _=globals: _())
'''

'''
Setup given globals
'''
def init(_globals):
    '''
    Jinja environment for jinja templates
    '''
    import re
    from .model import build_form_fields
    from jinja2 import Environment, Template
    env = Environment(extensions=['jinja2.ext.do'])
    env.filters['re_match'] = lambda target, expr: re.match(expr, str(target)).groups()
    env.globals.update(build_form_fields())

    '''
    Basic field_matcher regex to automatically search for Field
    definitions of the form:
    MyField(
    ...
    )
    '''
    field_match = re.compile(
        r'([A-Za-z_]+)\(',
        re.MULTILINE | re.DOTALL
    )

    '''
    IPython cell magic allows function to execute an entire cell.
    %%my_magic whatever
    all
    my
    data

    Results in a call:
    my_magic(
    "whatever",
    """all
        my
        data""")
    '''
    from IPython.core.magic import register_cell_magic
    from IPython.display import display, Markdown

    @register_cell_magic
    def nbtemplate(line, cell):
        '''
        Notebook Template Magic: See Steps for more information.
        Compile jinja2 into source code, and then evaluate that
        source code.
        '''

        '''
        Step 1. Render cell with jinja2, removing empty lines.
        execute or display the results, modifying a copy of the
        current python globals dict.
        '''
        global_internal = _globals()
        template = env.from_string(cell)
        rendered = '\n'.join(
            line
            for line in template.render().splitlines()
            if line.strip() != ''
        )
        if line == 'markdown':
            display(Markdown(rendered))
        elif line == 'code'  or line == 'hide_code':
            display(Markdown('```python\n%s\n```' % (rendered)))
        else:
            if line == 'code_eval' or line == 'hide_code_eval':
                display(Markdown('```python\n%s\n```' % (rendered)))
            exec(
                rendered,
                global_internal,
            )

        '''
        Step 2. Check for new variables in the internal global
        and pass them to the python global scope. Check for
        new variables in the jinja2 template and pass them to the
        template environment global so they are available in
        future jinja2 calls.
        '''
        for k, v in global_internal.items():
            if not k.startswith('_'):
                _globals()[k] = v

        for k, v in template.module.__dict__.items():
            if not k.startswith('_'):
                env.globals[k] = v
