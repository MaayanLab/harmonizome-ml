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

#%%nbtemplate hide
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
    from jinja2 import Environment, Template
    env = Environment(extensions=['jinja2.ext.do'])
    env.filters['re_match'] = lambda target, expr: re.match(expr, str(target)).groups()

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

    class Handler:
        '''
        Generic Field definition handler
        '''
        def __init__(self, **kwargs):
            for k,v in kwargs.items():
                setattr(self, k, v)
            if getattr(self, 'value', None) is None:
                self.value = getattr(self, 'default', None)
        def __str__(self):
            if type(getattr(self, 'choices', None)) == dict:
                choice = self.choices.get(self.value)
                if type(choice) == Handler:
                    return str(choice)
                else:
                    print(type(choice))
                return choice
            return str(self.value)
        __repr__ = __str__

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
        Compile jinja2 into source code containing arbitrary
        field definitions, injecting field-variables into the
        python global scope
        Caveat: Setting up a field should not occur in the same
        cell as using it in variable substitution. e.g.:

        %%nbtemplate
        Field(name='foo')
        # Can't use {{ foo }} here
        
        %%nbtemplate
        # Now it'll work
        print({{ foo }})
        
        Caveat: Object calls that aren't actually fields that haven't
        been defined globally will be treated as such and won't
        show any errors. This may make debugging why your statement
        isn't quite what you anticipated. This probably won't happen
        often. e.g.:
        
        #from math import sqrt # forgot to do import

        %%nbtemplate
        IntField(name='my_variable', default=100)
        
        # you could just use my_variable outside
        #  of template scope and avoid this issue
        %%nbtemplate 
        num = sqrt({{ my_variable.value }})
        
        print(num) # None
        '''
        global_internal = _globals()

        def handler(*kargs, **field):
            '''
            Handler: This function's call signature allows it
            to pretend to be ANY valid python function. If we
            have what seems like a field (given that name karg
            is available), we expose it to the jinja2 environment
            globals as a dict, and to the python environment
            globals as the current or default value.
            '''
            field_handler = Handler(**field)
            if getattr(field_handler, 'name', None) is None:
                return

            return field_handler

        '''
        Step 1. Find arbitrary function calls that aren't in the
        global scope and create the function using `handler` in
        the jinja2 environment scope.
        '''
        for m in field_match.finditer(cell):
            field = m.group(1)
            if global_internal.get(field, None) is None:
                env.globals[field] = handler
            elif env.globals.get(field, None) is not None:
                del env.globals[field]

        '''
        Step 2. Create an internal global dict containing both
        our jinja2 environment globals and python globals to
        be used for execution of the jinja2-compiled source.
        '''
        
        template = env.from_string(cell)
        rendered = '\n'.join(
            line
            for line in template.render().splitlines()
            if line.strip() != ''
        )
        if line == 'markdown':
            display(Markdown(rendered))
        elif line == 'code':
            display(Markdown('```python\n%s\n```' % (rendered)))
        else:
            if line == 'code_eval':
                display(Markdown('```python\n%s\n```' % (rendered)))
            exec(
                rendered,
                global_internal,
            )

        '''
        Step 3. Check for new variables in the internal global
        and pass them to the python global scope. Check for
        new variables in the template and pass them to the
        environment global scope.
        '''
        for k, v in global_internal.items():
            if not k.startswith('_'):
                _globals()[k] = v

        for k, v in template.module.__dict__.items():
            if not k.startswith('_'):
                env.globals[k] = v
