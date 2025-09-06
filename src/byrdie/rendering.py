import json
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
            component_name: instance,
            'object': instance,
            'variant': variant
        }

        html = render_to_string(template_name, context)

        # Prepare data for the frontend bridge
        exposed_data = {}
        if hasattr(instance, 'exposed_fields'):
            for field_name in instance.exposed_fields:
                exposed_data[field_name] = getattr(instance, field_name)

        for name in dir(instance):
            if not name.startswith('_'):
                try:
                    attr = getattr(instance, name)
                    if callable(attr) and hasattr(attr, '_byrdie_exposed'):
                        # How to handle methods will be defined in a later task.
                        # For now, we just indicate that they are available.
                        exposed_data[name] = True
                except AttributeError:
                    # This can happen with managers, so we just ignore it.
                    pass

        if exposed_data:
            # Inject x-data into the root element
            json_data = json.dumps(exposed_data)
            # This is a bit fragile, but avoids a dependency on a full HTML parser.
            # It assumes the first tag is the root element.
            import re
            html = re.sub(r'<([a-zA-Z0-9\-]+)', f'<\\1 x-data=\'{json_data}\'', html, 1)

        return mark_safe(html)

    except TemplateDoesNotExist:
        return mark_safe(f"<!-- Component template not found: {template_name} -->")
