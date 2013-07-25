import os
import sys

from setuptools import setup, find_packages

BASE_PACKAGE = 'djfixture'
version = __import__(BASE_PACKAGE).get_version()

install_requires = [
	'django>=1.4,<1.6',
]

kwargs = {
    'packages': find_packages(exclude=['tests', '*.tests', '*.tests.*', 'tests.*']),
    'include_package_data': True,

    'install_requires': install_requires,

    'test_suite': 'test_suite',

    'tests_require': [
	'coverage',
    ],

    'version': version,
    'name': 'django-fixture',
    'author': 'Daniel Megahan, Byron Ruth',
    'author_email': 'megahand@email.chop.edu, ruthb@email.chop.edu',
    'description': 'Utilities for generating django fixtures from a csv data file and django model JSON schema',
    'license': 'BSD',
    'keywords': 'fixture JSON django utils',
    'url': 'https://github.com/cbmi/djFixture/',

    'install_requires': ['distribute', 'django'],

    'classifiers': [
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ],
}

setup(**kwargs);
