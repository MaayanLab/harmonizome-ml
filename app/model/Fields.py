import os
import re
import json
from copy import copy
from flask import render_template, Markup
from ..util import globalContext, data_dir

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
        field_name: lambda _field=field, _context=context, name=None, **kwargs: _field(**dict(kwargs, name=name, value=_context.get(name)))
        for field_name, field in fields.items()
    }

class Field:
    def __init__(self, group=None, name=None, label=None, value=None, choices=None, default=None, **kwargs):
        self.args = dict(
            group=group,
            name=name,
            choices=choices,
            label=label,
            value=value,
            default=default,
            **kwargs,
        )
        self.value = value if value is not None else default
    
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
    
    def choices(self):
        choices = self.args.get('choices', [])
        if type(choices) == dict:
            return choices.keys()
        else:
            return choices

    def constraint(self, value):
        return value in self.choices()

    def get_value(self, value):
        choices = self.args.get('choices', [])
        if type(choices) == dict:
            return choices[value]
        else:
            return value

    def safe_value(self, value):
        if self.constraint(value):
            return Markup(self.get_value(value))
        raise Exception('%s constraint not satisfied' % (self.args['label']))

    def __str__(self):
        return self.safe_value(self.value)

@register
class StringField(Field):
    def __init__(self, constraint=r'.*', hint=None, **kwargs):
        super(StringField, self).__init__(
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
    pass

@register
class MultiChoiceField(Field):
    def get_value(self, value):
        if type(value) == str:
            return [super(MultiChoiceField, self).get_value(value)]
        elif type(value) == list:
            return [super(MultiChoiceField, self).get_value(v) for v in value]
        elif value is None:
            return []
        else:
            raise Exception("Invalid MultiChoiceField type")

    def constraint(self, value):
        for v in self.get_value(value):
            return super(MultiChoiceField, self).constraint(v)
        return True

@register
class IntField(Field):
    def __init__(self, min=0, max=10, **kwargs):
        super(IntField, self).__init__(
            min=min,
            max=max,
            **kwargs,
        )
    
    def get_value(self, value):
        if type(value) == str:
            return int(value)
        return value

    def choices(self):
        return list(range(self.args['min'], self.args['max']))
    
    def constraint(self, value):
        val = self.get_value(value)
        return val >= self.args['min'] and val <= self.args['max']

@register
class BoolField(Field):
    def choices(self):
        return [True, False]

@register
class TextField(StringField):
    pass

@register
class TextListField(TextField):
    def get_value(self, value):
        return Markup(value.split('\n'))

@register
class SearchField(StringField):
    def __init__(self, hints=[], **kwargs):
        super(SearchField, self).__init__(
            hints=hints,
            **kwargs,
        )

@register
class TargetClassSearchField(SearchField):
    def get_field(self):
        return 'SearchField'

    def choices(self):
        return json.load(open(data_dir + '/class_list.json', 'r'))

@register
class TargetGeneSearchField(SearchField):
    def get_field(self):
        return 'SearchField'

    def choices(self):
        return json.load(open(data_dir + '/gene_list.json', 'r'))

@register
class TargetField(Field):
    pass

@register
class SectionField(Field):
    def __init__(self, content='', **kwargs):
        super(SectionField, self).__init__(
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
        super(DescriptionField, self).__init__(
            content=content,
            **kwargs,
        )

    def render(self):
        return self.args['content']

    def safe_value(self, value):
        return Markup(self.args['content'])

