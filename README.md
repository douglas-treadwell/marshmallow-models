Marshmallow Models
==================


Inspired by [Schematics](https://github.com/schematics/schematics).

Whereas Marshmallow is an excellent serialization/deserialization
and validation library, it wasn't intended to be a class or type
definition library, which Schematics was.

This library provides a Schematics-like Model but
using Marshmallow's Fields and validation.


Usage
-----

Models are defined like Schemas, but whereas a Schema is instantiated
with parameters and then used to schema.dump(data) or schema.load(data),
or schema.validate(data),
Models are instantiated, attributes may be assigned to them, and then
they can be .dump()'d, .dumps()'d or .validate()'d.

```python
from marshmallow_models import Model
from marshmallow.fields import String, Integer

class PersonModel(Model):
    name = String(required=True, default='Anonymous')
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

Configuration
-------------

Marshmallow Models support the "class Meta" configuration method,
and also support defining the "class Meta" using the alias
"class Options".
