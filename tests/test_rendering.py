from django.test import TestCase
from django.db import models
from django.template import Template, Context
from byrdie.rendering import render_component
from .models import Note, ExposedModel
import os
import json

class RenderingTest(TestCase):
    def setUp(self):
        self.template_dir = 'components'
        os.makedirs(self.template_dir, exist_ok=True)

        self.default_template_path = os.path.join(self.template_dir, 'note.html')
        with open(self.default_template_path, 'w') as f:
            f.write('<h1>{{ object.content }}</h1>')

        self.card_template_path = os.path.join(self.template_dir, 'note_card.html')
        with open(self.card_template_path, 'w') as f:
            f.write('<h2>{{ object.content }}</h2>')

        self.exposed_template_path = os.path.join(self.template_dir, 'exposedmodel.html')
        with open(self.exposed_template_path, 'w') as f:
            f.write('<div>{{ object.name }}</div>')

    def tearDown(self):
        os.remove(self.default_template_path)
        os.remove(self.card_template_path)
        os.remove(self.exposed_template_path)

    def test_render_component_with_exposed_data(self):
        instance = ExposedModel.objects.create(name='Test', value=42)
        rendered_html = render_component(instance)

        expected_data = {'name': 'Test', 'value': 42, 'double': True}
        expected_json = json.dumps(expected_data)

        self.assertIn(f"x-data='{expected_json}'", rendered_html)
        self.assertIn('>Test</div>', rendered_html)

    def test_render_component_direct_call(self):
        instance = Note.objects.create(content='Test Content')
        rendered_html = render_component(instance)
        self.assertEqual(rendered_html.strip(), '<h1>Test Content</h1>')

    def test_component_tag(self):
        instance = Note.objects.create(content='Tag Test')
        template = Template("{% load byrdie_tags %}{% component 'instance' %}")
        context = Context({'instance': instance})
        rendered_html = template.render(context)
        self.assertEqual(rendered_html.strip(), '<h1>Tag Test</h1>')

    def test_named_component(self):
        instance = Note.objects.create(content='Card Test')
        template = Template("{% load byrdie_tags %}{% component 'instance:card' %}")
        context = Context({'instance': instance})
        rendered_html = template.render(context)
        self.assertEqual(rendered_html.strip(), '<h2>Card Test</h2>')

    def test_invalid_variant(self):
        instance = Note.objects.create(content='Invalid Variant Test')
        template = Template("{% load byrdie_tags %}{% component 'instance:invalid' %}")
        context = Context({'instance': instance})
        rendered_html = template.render(context)
        self.assertEqual(rendered_html.strip(), "<!-- Component variant 'invalid' not allowed for model 'note' -->")

    def test_render_component_not_found(self):
        class AnotherModel(models.Model):
            class Meta:
                app_label = 'tests'

        instance = AnotherModel()
        rendered_html = render_component(instance)
        self.assertEqual(rendered_html.strip(), '<!-- Component template not found: anothermodel.html -->')
