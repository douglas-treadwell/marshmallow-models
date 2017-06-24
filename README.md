Marshmallow Models
==================


Installation
------------

```
pip install marshmallow-models
```


Contributing
------------

Feature requests, feedback,
[issues](https://github.com/douglas-treadwell/marshmallow-models/issues),
and pull requests are welcome and appreciated.

Please follow the [Marshmallow Contributing Guidelines](
https://github.com/marshmallow-code/marshmallow/blob/dev/CONTRIBUTING.rst
).


Overview
--------

Inspired by [Schematics](https://github.com/schematics/schematics),
powered by [Marshmallow](https://github.com/marshmallow-code/marshmallow).

Whereas Marshmallow is an excellent serialization/deserialization
and validation library, it wasn't intended to be a class or type
definition library, which Schematics was.

This library provides a Schematics-like Model but
using Marshmallow's Fields and validation.  This library also
intentionally maintains the usage style of marshmallow so that
users of Marshmallow Schemas will be able to use these Models easily.

Usage
-----

Models are defined like Schemas, but whereas a Schema is instantiated
with parameters and then used to schema.dump(data) or schema.load(data),
or schema.validate(data),
Models are instantiated, attributes may be assigned to them, and then
they can be .dump()'d, .dumps()'d or .validate()'d.

### Basic Usage

```python
from marshmallow_models import Model
from marshmallow.fields import String, Integer

class PersonModel(Model):
    name = String(required=True)
    age = Integer(required=True)

person = PersonModel()

person.name = 'Tester'
person.age = 100

# or equivalently:
person = PersonModel({'name': 'Tester', 'age': 100})

# or equivalently:
person = PersonModel(name='Tester', age=100)

# throws marshmallow.exceptions.ValidationError if invalid
person.validate()

person.dump().data  # {'name': 'Tester', 'age': 100}
```

### Missing and Default Attributes

```python
class PersonModel(Model):
    name = String(missing='Anonymous')
    age = Integer(default=0)

person = PersonModel()

person.name  # 'Anonymous'
person.age  # 0
```

Default and missing parameters may be provided as they are to
Marshmallow Schemas.

Constructing a model is treated like
"loading" data (as in, schema.load(data)).  If attributes are
missing and a `missing` configuration was provided, those values
will be assigned to the missing attributes.

Reading attributes is treated like "dumping" data (as in,
schema.dump(data)), as are calls to model.dump() and dumps().
If a value doesn't exist when read or dumped, the default value
will be substituted for that attribute.

In many cases `default` and `missing` can be used interchangeably
in the context of Models, but there may be cases where their
different treatment is meaningful.

### Nested Models

Nested models are also supported.

```python
class ParentModel(PersonModel):
    child = NestedModel(PersonModel)

parent = ParentModel(name='Tester', age=40, child=dict(name='Child', age=10))

self.assertEqual(parent.child.name, 'Child')

parent.child.name = 'Kid'

self.assertEqual(parent.child.name, 'Kid')
```

Configuration
-------------

Marshmallow Models support the "class Meta" configuration method.

An additional Meta attribute is supported: `strict_constructor`.

In Marshmallow Schemas, transformation of input data to output data
was a single step process.  In Marshmallow Models, it might be
reasonable for users to instantiate a model with incomplete attributes
and then fill in the attributes before attempting to validate() or
dump() the data.

By default, even for Models with `strict = True`
the constructor does not raise exceptions for incomplete attributes.
If exceptions are wanted in this case, set `strict_constructor = True`.


```python
class PersonWithStrictConstructorModel(Model):
    class Meta:
        strict_constructor = True

    name = String(required=True)
    age = Integer(required=True)

with self.assertRaises(ValidationError):
    person = PersonWithStrictConstructorModel()
```
