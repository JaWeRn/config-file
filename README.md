# Config File

> Modify configuration files of various formats with the same simple API

![Python Version](https://img.shields.io/pypi/pyversions/config-file.svg)
[![Version](https://img.shields.io/pypi/v/config-file)](https://pypi.org/project/config-file/)
[![Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://pypi.org/project/black/)
[![Documentation Status](https://readthedocs.org/projects/config-file/badge/?version=latest)](https://config-file.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://github.com/eugenetriguba/config-file/workflows/python%20package%20CI/badge.svg?branch=master)](https://github.com/eugenetriguba/config-file/actions/)
[![Codecov](https://codecov.io/gh/eugenetriguba/config-file/graph/badge.svg)](https://codecov.io/gh/eugenetriguba/config-file)

## About Config File

The Config File project is designed to allow you to easily manipulate your
configuration files with the same simple API whether they are in INI, JSON,
YAML, or TOML.

## Installation

Config File is available to download through PyPI.

```bash
$ pip install config-file
```

### Installing Extras

If you want to manipulate YAML and TOML, you'll want to download the extras as well.

```bash
$ pip install config-file[yaml, toml]
```

You can also use [Poetry](https://python-poetry.org).

```bash
$ poetry install config-file -E yaml -E toml
```

## Usage Overview

For this overview, let's say you have the following `ini` file
you want to manipulate.

```ini
[section]
num_key = 5
str_key = blah
bool_key = true
list_key = [1, 2]

[second_section]
dict_key = { "another_num": 5 }
```

It must have a `.ini` extension in order
for the package to recognize it and use the correct parser for it.

### Setting up ConfigFile

To use the package, we import in the `ConfigFile` object.

We can set it up by giving it a string or `pathlib.Path` as the argument.
Any home tildes `~` in the string or `Path` are recognized and converted
to the full path for us.

```python
from config_file import ConfigFile

config = ConfigFile("~/some-project/config.ini")
```

### Using `get()`

A recurring pattern you'll see here is that all methods that
need to specify something inside your configuration file will
do so using a dot syntax.

#### Retrieving keys and sections

So to retrieve our `num_key`, we'd specify the heading and the
key separated by a dot. All values will then be retrieved as
strings.

```python
config.get('section.num_key')
>>> '5'
```

While we can retrieves keys, we can also retrieve the entire
section, which will be returned back to us as a dictionary.

```python
config.get('section')
>>> {'num_key': '5', 'str_key': 'blah', 'bool_key': 'true', 'list_key': '[1, 2]'}
```

#### Coercing the return types

However, some of these keys are obviously not strings natively.
If we are retrieving a particular value of a key, we may want to
coerce it right away without doing clunky type conversions after
each time we retrieve a value. To do this, we can utilize the
`return_type` keyword argument.

```python
config.get('section.num_key', return_type=int)
>>> 5
```

Sometimes we don't have structures quite that simple though. What
if we wanted all the values in `section` coerced? For that, we can
utilize a `parse_types` keyword argument.

```python
config.get('section', parse_types=True)
>>> {'num_key': 5, 'str_key': 'blah', 'bool_key': True, 'list_key': [1, 2]}
```

It also works for regular keys.

```python
config.get('section.num_key', parse_types=True)
>>> 5
```

#### Handling non-existent keys

Sometimes we want to retrieve a key but are unsure of if it will exist.
There are two ways we could handle that.

The first is the one we're used to seeing: catch the error.

```python
from config_file import MissingKeyError

try:
    important_value = config.get('section.i_do_not_exist')
except MissingKeyError:
    important_value = 42
```

However, the `get` method comes with a `default` keyword argument that we
can utilze for this purpose.

```python
config.get('section.i_do_not_exist', default=42)
>>> 42
```

This can be handy if you have a default for a particular configuration value.

### Using `set()`

We can use `set()` to set a existing key's value.

```python
config.set('section.num_key', 6)
```

The method does not return anything, since there is nothing
useful to return. If something goes wrong where it is unable to set
the value, an exception will be raised instead. This is the case
for most methods on `ConfigFile`, such as `delete()` or `save()`,
where there would be no useful return value to utilize.

With `set()`, we can also create and set keys that don't exist yet.

```python
config.set('new_section.new_key', 'New key value!')
```

Would then result in the following section being added to our original file:

```ini
[new_section]
new_key = New key value!
```

The exact behavior of how these new keys or sections are added are a bit
dependent on the file format we're using, since every format is a little
different in it's structure and in what it supports. See the
[full documentation](#Documentation) for more information there.

### Using `delete()`

`delete()` allows us to delete entire sections or specific keys.

```python
config.delete('section')
```

Would result in the entire section being removed from our configuration file.
However, we can also just delete a single key.

```python
config.delete('section.num_key')
```

### Using `has()`

`has()` allows us to check whether a given key exists in our file. There
are two ways to use `has()`.

The first is using the dot syntax.

```python
config.has('section.str_key')
>>> True
config.has('does_not_exist')
>>> False
```

This will check if our specific key or section exists. However, we can
also check in general if a given key or sections exists anywhere in our
file with the `wild` keyword argument.

```python
config.has('str_key', wild=True)
>>> True
```

### Using `save()`

For any changes we make to our configuration file, they are not written out
to the filesystem until we call `save()`. This is to avoid unnecessary write
calls after each operation until we actually need to save.

```python
config.delete('section.list_key')
config.save()
```

### Using `stringify()`

`stringify()` shows us our configuration file, with any changes we've made,
as a string. `stringify()` will always show us our latest changes since it
is stringify-ing our internal representation of the configuration file, not
just the file we've read in.

```python
config.stringify()
>>> '[section]\nnum_key = 5\nstr_key = blah\nbool_key = true\nlist_key = [1, 2]\n\n[second_section]\ndict_key = { "another_num": 5 }\n\n'
```


### Using `restore_original()`

If we have a initial configuration file state, we could keep a copy of that
initial file and restore back to it whenever needed using `restore_original()`.

By default, if we created our `ConfigFile` object with the path of `~/some-project/config.ini`,
`restore_original()` will look for our original file at `~/some-project/config.original.ini`.

```python
config.restore_original()
```

However, if we have a specific path elsewhere that this original configuration file is or it
is named differently than what the default expects, we can utilize the `original_file_path`
keyword argument.

```python
config.restore_original(original_file_path="~/some-project/original-configs/config.ini")
```


## Documentation

Full documentation and API reference is available at https://config-file.readthedocs.io

## License

The [MIT](https://github.com/eugenetriguba/config-file/blob/master/LICENSE) License.
