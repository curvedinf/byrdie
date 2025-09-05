from django.db import models
from django.template.loader import render_to_string, TemplateDoesNotExist
from django.utils.safestring import mark_safe

def render_component(instance: models.Model, variant: str = None) -> str:
    """
    Renders a component for a given model instance.
    """
    component_name = instance.__class__.__name__.lower()

    if variant:
        # Check if the variant is allowed for this model
        if not hasattr(instance, 'components') or variant not in instance.components:
            return mark_safe(f"<!-- Component variant '{variant}' not allowed for model '{component_name}' -->")
        template_name = f'{component_name}_{variant}.html'
    else:
        template_name = f'{component_name}.html'

    try:
        # Pass the instance and variant to the template context
        context = {
            'object': instance,
            'variant': variant
        }
        return render_to_string(template_name, context)
    except TemplateDoesNotExist:
        return mark_safe(f"<!-- Component template not found: {template_name} -->")
