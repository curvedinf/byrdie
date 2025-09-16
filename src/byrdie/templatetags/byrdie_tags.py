from django import template
from django.apps import apps
from django.template import Node, TemplateSyntaxError
from django.utils.safestring import mark_safe
import re

from byrdie.rendering import render_component

register = template.Library()

@register.simple_tag(takes_context=True)
def component(context, component_string):
    """
    Renders a component.
    Usage: {% component 'note' %} or {% component 'note:card' %}
    """
    if ':' in component_string:
        instance_name, variant = component_string.split(':')
    else:
        instance_name = component_string
        variant = None

    if instance_name not in context:
        raise TemplateSyntaxError(f"Component instance '{instance_name}' not found in context.")

    instance = context[instance_name]

    return render_component(instance, variant=variant)


class ByrdieNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
        self.model_names = [model.__name__.lower() for model in apps.get_models()]

    def render(self, context):
        output = self.nodelist.render(context)

        if not self.model_names:
            return output

        model_names_pattern = '|'.join(self.model_names)
        # This regex looks for self-closing tags like <note instance="..." />
        regex = re.compile(
            r'<(?P<tag_name>' + model_names_pattern + r')\s+'
            r'instance=["\'](?P<instance_name>.*?)["\']'
            r'(?:\s+variant=["\'](?P<variant>.*?)["\'])?'
            r'[^>]*?/>'
        )

        def replace_component_tag(match):
            instance_name = match.group('instance_name')
            variant = match.group('variant')

            try:
                # Resolve the instance from the context. It could be a variable.
                instance = template.Variable(instance_name).resolve(context)
            except template.VariableDoesNotExist:
                # Fallback to checking the context directly
                if instance_name in context:
                    instance = context[instance_name]
                else:
                    return f"<!-- Byrdie instance '{instance_name}' not found in context -->"

            return render_component(instance, variant=variant)

        output = regex.sub(replace_component_tag, output)
        return mark_safe(output)

@register.tag(name="byrdie")
def byrdie(parser, token):
    """
    Activates the Byrdie frontend bridge.
    Usage: {% byrdie %}... template content with <model ... /> tags ...{% endbyrdie %}
    """
    nodelist = parser.parse(('endbyrdie',))
    parser.delete_first_token()
    return ByrdieNode(nodelist)

import json
from byrdie.api import api

@register.simple_tag
def byrdie_api_routes():
    """
    Outputs a script tag with a JSON object of the API routes.
    """
    api_routes = {}
    for path, view in api.router.routes.items():
        if path.startswith('/api'):
            original_view = view
            while hasattr(original_view, '__wrapped__'):
                original_view = original_view.__wrapped__

            js_name = original_view.__name__.replace('__', '.')
            api_routes[js_name] = path

    return mark_safe(f'<script>window.byrdie_routes = {json.dumps(api_routes)};</script>')
