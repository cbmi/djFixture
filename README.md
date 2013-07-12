django-redcap
=============

Utilities for generating django fixtures from a csv data file and json file

What it does
------------

[Djredcap] (https://github.com/dmegahan/django-redcap) and [djfixture] (https://github.com/cbmi/djFixture) are 2 scripts that automate the process of transferring patient or survey data from Redcap to Harvest. The programs work alongside one another to create a models.py file, a fixtures.json file and a filename.json file. 


Djfixture uses a csv containing the data used for the fixtures and the intermediary json file created from djredcap. Djfixture looks at each field in each form from the json file, repeats them if needed, and uses their form name and other clues to determine the name of the field in the data file using clues from its form name, its number of choices, and extracts that data. 

Install and Setup
-----------------

To install:

```bash
python setup.py sdist
cd dist
tar xvfz django-fixture-0.1.1b2
cd django-fixture-0.1.1b2
python setup.py install --user
```

Once installed, simply add `djfixture` to your `INSTALLED_APPS` project settings:

```python
INSTALLED_APPS = (
    'djfixture',
    ...
)
```

Commands
--------

Djredcap and djfixture function alongside one another. For both of them to work correctly, they must be run in the correct order. djredcap should be run first. Djredcap creates an intermediary json file that describes each form, including each field and its information, from the redcap data dictionary submitted in djredcap. This json file is used in djfixture to describe the models.py file.

Commands are executed using the `fixture` command with a sub-command, e.g.:

```bash
./manage.py fixture [options] subcommand [args]
```

**inspect**

```bash
./manage.py fixture inspect path/to/exported/data.csv path/to/djredcap/file.json
```

