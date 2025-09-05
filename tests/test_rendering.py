from django.test import TestCase
from django.db import models
from django.template import Template, Context
from byrdie.rendering import render_component
import os

# Create a dummy model for testing
class TestComponentModel(models.Model):
    name = models.CharField(max_length=100)
    components = ['card']

    class Meta:
        app_label = 'tests'

class RenderingTest(TestCase):
    def setUp(self):
        self.template_dir = 'components'
        os.makedirs(self.template_dir, exist_ok=True)

        self.default_template_path = os.path.join(self.template_dir, 'testcomponentmodel.html')
        with open(self.default_template_path, 'w') as f:
            f.write('<h1>{{ object.name }}</h1>')

        self.card_template_path = os.path.join(self.template_dir, 'testcomponentmodel_card.html')
        with open(self.card_template_path, 'w') as f:
            f.write('<h2>{{ object.name }}</h2>')

    def tearDown(self):
        os.remove(self.default_template_path)
        os.remove(self.card_template_path)

    def test_render_component_direct_call(self):
        instance = TestComponentModel.objects.create(name='Test Name')
        rendered_html = render_component(instance)
        self.assertEqual(rendered_html.strip(), '<h1>Test Name</h1>')

    def test_component_tag(self):
        instance = TestComponentModel.objects.create(name='Tag Test')
        template = Template("{% load byrdie_tags %}{% component 'instance' %}")
        context = Context({'instance': instance})
        rendered_html = template.render(context)
        self.assertEqual(rendered_html.strip(), '<h1>Tag Test</h1>')

    def test_named_component(self):
        instance = TestComponentModel.objects.create(name='Card Test')
        template = Template("{% load byrdie_tags %}{% component 'instance:card' %}")
        context = Context({'instance': instance})
        rendered_html = template.render(context)
        self.assertEqual(rendered_html.strip(), '<h2>Card Test</h2>')

    def test_invalid_variant(self):
        instance = TestComponentModel.objects.create(name='Invalid Variant Test')
        template = Template("{% load byrdie_tags %}{% component 'instance:invalid' %}")
        context = Context({'instance': instance})
        rendered_html = template.render(context)
        self.assertEqual(rendered_html.strip(), "<!-- Component variant 'invalid' not allowed for model 'testcomponentmodel' -->")

    def test_render_component_not_found(self):
        class AnotherModel(models.Model):
            class Meta:
                app_label = 'tests'

        instance = AnotherModel()
        rendered_html = render_component(instance)
        self.assertEqual(rendered_html.strip(), '<!-- Component template not found: anothermodel.html -->')
