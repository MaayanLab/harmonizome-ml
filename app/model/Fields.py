import os
import re
import json
from copy import copy
from flask import render_template, Markup
from util import globalContext

fields = {}
def register(field):
    fields[field.__name__] = field
    return field

def build_form_fields():
    return {
        name: lambda _field=field, **kwargs: _field(**kwargs)#.render()
        for name, field in fields.items()
    }

def build_safe_value(context):
    return {
        field_name: lambda _field=field, _context=context, name=None, **kwargs: _field(**kwargs).safe_value(_context.get(name))
        for field_name, field in fields.items()
    }

class Field:
    def __init__(self, group=None, name=None, label=None, **kwargs):
        self.args = dict(
            group=group,
            name=name,
            label=label,
            **kwargs,
        )
    
    def get_field(self):
        return self.__class__.__name__

    def get_template(self):
        return os.path.join('ipynb', 'form', self.get_field() + '.j2')

    def render(self):
        return Markup(render_template(
            self.get_template(),
            **self.args,
            **globalContext,
        ))
    
    def constraint(self, value):
        return False
    
    def value(self, value):
        return value

    def safe_value(self, value):
        if self.constraint(value):
            return Markup(self.value(value))
        raise Exception('%s constraint not satisfied' % (self.args['label']))

@register
class StringField(Field):
    def __init__(self, constraint=r'.*', hint=None, **kwargs):
        super().__init__(
            constraint=constraint,
            hint=hint,
            **kwargs,
        )

    def constraint(self, value):
        if value is None:
            raise Exception('%s cannot be empty' % (self.args['label']))
        return re.match(self.args['constraint'], value)

@register
class ChoiceField(Field):
    def __init__(self, choices=[], **kwargs):
        super().__init__(
            choices=choices,
            **kwargs,
        )

    def value(self, value):
        if type(self.args['choices']) == dict:
            return self.args['choices'][value]
        else:
            return value
    
    def constraint(self, value):
        if type(self.args['choices']) == dict:
            return value in self.args['choices'].keys()
        elif type(self.args['choices']) == list:
            return value in self.args['choices']

@register
class MultiChoiceField(ChoiceField):
    def value(self, value):
        if type(value) == str:
            return [value]
        elif type(value) == list:
            return value
        elif value is None:
            return []
        else:
            raise Exception("Invalid MultiChoiceField type")

    def constraint(self, value):
        for v in self.value(value):
            if v not in self.args['choices']:
                return False
        return True

@register
class IntField(Field):
    def __init__(self, min=0, max=10, **kwargs):
        super().__init__(
            min=min,
            max=max,
            **kwargs,
        )

    def constraint(self, value):
        try:
            int(value)
            return True
        except:
            return False

@register
class TextField(StringField):
    pass

@register
class TextListField(TextField):
    def value(self, value):
        return Markup(value.split('\n'))

@register
class SearchField(StringField):
    def __init__(self, hints=[], **kwargs):
        super().__init__(
            hints=hints,
            **kwargs,
        )

@register
class TargetClassSearchField(SearchField):
    def __init__(self, constraint=r'.*', **kwargs): # ^[A-Za-z0-9- \(\),\']+ \([A-Za-z ] from [A-Za-z- ]\)$
        super().__init__(
            constraint=constraint,
            **kwargs,
        )

    def get_field(self):
        return 'SearchField'

@register
class SectionField(Field):
    def __init__(self, content='', **kwargs):
        super().__init__(
            content=content,
            **kwargs,
        )

    def is_section(self):
        return True

    def render(self):
        return self.args['content']

    def safe_value(self, value):
        return Markup(self.args['content'])

@register
class LaunchField(SectionField):
    def get_field(self):
        return 'SectionField'

@register
class DescriptionField(Field):
    def __init__(self, content='', **kwargs):
        super().__init__(
            content=content,
            **kwargs,
        )

    def render(self):
        return self.args['content']

    def safe_value(self, value):
        return Markup(self.args['content'])

