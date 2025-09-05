from django import template
from django.template import TemplateSyntaxError
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
