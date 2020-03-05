import os
import re
import json
from copy import copy
from flask import render_template, Markup
from ..util import globalContext, data_dir

fields = {}
def register(field):
    ''' Register a field for usage in templates
    '''
    fields[field.__name__] = field
    return field

def build_fields(context={}):
    ''' Build a dictionary of Field instances
    '''
    global fields
    return {
        field_name: lambda name=None, _field=field, _context=context, **kwargs: _field(
            **dict(kwargs,
                name=name,
                value=_context.get(name),
            )
        )
        for field_name, field in fields.items()
    }

class Field:
    def __init__(self,
            group=None,
            name=None,
            label=None,
            value=None,
            choices=[],
            default=None,
            **kwargs):
        self.args = dict(
            group=group,
            name=name,
            choices=choices,
            label=label,
            default=default,
            value=value if value is not None else default,
            **kwargs,
        )

    def constraint(self):
        ''' Return true if args.value satisfies constraints.
        '''
        return self.args['value'] in self.choices

    def render(self):
        ''' Return a rendered version of the field (form)
        '''
        return Markup(
            render_template(
                self.template,
                this=self,
                **globalContext,
            )
        )

    @property
    def field(self):
        ''' Field name
        '''
        return self.__class__.__name__

    @property
    def template(self):
        ''' Template to use for rendering field
        '''
        return os.path.join('ipynb', 'form', self.field + '.j2')

    @property
    def choices(self):
        ''' Potential values to choose from
        '''
        choices = self.args.get('choices')
        if type(choices) == dict:
            return choices.keys()
        else:
            return choices

    @property
    def raw_value(self):
        ''' Raw value of the field
        '''
        return self.args['value']

    @property
    def value(self):
        ''' Effective value of the field when used
        '''
        choices = self.args.get('choices')
        if type(choices) == dict:
            return choices[self.raw_value]
        else:
            return self.raw_value

    @property
    def safe_value(self):
        ''' Effective value ready to be displayed
        '''
        assert self.constraint(), '%s[%s] (%s) does not satisfy constraints' % (
            self.field, self.args.get('name', ''), self.value
        )
        return Markup(self.value)

    def __str__(self):
        return self.safe_value

@register
class StringField(Field):
    def __init__(self, constraint=r'.*', hint=None, **kwargs):
        super(StringField, self).__init__(
            constraint=constraint,
            hint=hint,
            **kwargs,
        )

    def constraint(self):
        return self.raw_value is not None and re.match(self.args['constraint'], self.raw_value)

@register
class ChoiceField(Field):
    pass

@register
class MultiChoiceField(Field):
    @property
    def raw_value(self):
        if type(self.args['value']) == str:
            return [self.args['value']]
        elif type(self.args['value']) == list:
            return self.args['value']
        elif self.args['value'] is None:
            return []
        else:
            return None

    def constraint(self):
        return self.raw_value is not None and all(v in self.choices for v in self.raw_value)

@register
class IntField(Field):
    def __init__(self, min=0, max=10, **kwargs):
        super(IntField, self).__init__(
            min=min,
            max=max,
            **kwargs,
        )

    @property
    def raw_value(self):
        return int(self.args['value'])

    @property
    def choices(self):
        return list(range(self.args['min'], self.args['max']))

    def constraint(self):
        return self.raw_value >= self.args['min'] and self.raw_value <= self.args['max']

@register
class BoolField(Field):
    @property
    def raw_value(self):
        return self.args['value'] if type(self.args['value']) == bool else bool(json.loads(self.args['value'].lower()))

    @property
    def choices(self):
        return [True, False]

@register
class TextField(StringField):
    pass

@register
class FileField(StringField):
    pass

@register
class TextListField(TextField):
    @property
    def raw_value(self):
        return self.args['value'].split('\n')

@register
class SearchField(StringField):
    def __init__(self, hints=[], **kwargs):
        super(SearchField, self).__init__(
            hints=hints,
            **kwargs,
        )

@register
class TargetClassSearchField(SearchField):
    @property
    def field(self):
        return 'SearchField'

    @property
    def choices(self):
        return json.load(open(data_dir + '/class_list.json', 'r'))

@register
class TargetGeneSearchField(SearchField):
    @property
    def field(self):
        return 'SearchField'

    @property
    def choices(self):
        return json.load(open(data_dir + '/gene_list.json', 'r'))

@register
class TargetField(Field):
    pass

class ContentField(Field):
    def __init__(self, content='', **kwargs):
        super(ContentField, self).__init__(
            content=content,
            **kwargs,
        )

    def render(self):
        return self.args['content']

    @property
    def raw_value(self):
        return self.args['content']
    
    def constraint(self):
        return True

@register
class SectionField(ContentField):
    def is_section(self):
        return True

@register
class LaunchField(SectionField):
    @property
    def field(self):
        return 'SectionField'

@register
class DescriptionField(ContentField):
    pass
