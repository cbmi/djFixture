django-redcap
=============

Utilities for generating django fixtures from a csv data file and json file

Install and Setup
-----------------

django-redcap is available on [PyPi][0]. Use Pip to install it:

```bash
pip install django-fixture
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
Commands are executed using the `fixture` command with a sub-command, e.g.:

```bash
./manage.py fixture [options] subcommand [args]
```

**inspect**

```bash
./manage.py fixture inspect data.csv jsonmodel.json
```
