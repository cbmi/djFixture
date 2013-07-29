import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'tests.db',
    }
}

INSTALLED_APPS = (
    'djfixture',
    'tests',
)

SECRET_KEY = 'xSECRETx'
