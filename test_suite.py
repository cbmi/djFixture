import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'djfixture.tests.settings'

from django.core import management

apps = [
	'test',
]

management.call_command(*apps);
