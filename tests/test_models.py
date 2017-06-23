from unittest import TestCase
from marshmallow import Schema
from marshmallow_models import Model
from marshmallow.fields import String, Integer
from marshmallow.exceptions import ValidationError


# Schemas are here only to compare with Model schemas

class PersonSchema(Schema):
    name = String(required=True)
    age = Integer(required=True)


class ParentSchema(PersonSchema):
    num_children = Integer(required=True)


class PersonModel(Model):
    name = String(required=True)
    age = Integer(required=True)

    def __str__(self):
        return '%s, %s' % (self.name, self.age)


class ParentModel(PersonModel):
    num_children = Integer(required=True)


class TestModel(TestCase):
    def test_construction(self):
        person = PersonModel(dict(name='Tester', age=100))

        self.assertEqual(person.name, 'Tester')
        self.assertEqual(person.age, 100)

    def test_assignment_after_construction(self):
        person = PersonModel()

        person.name = 'Tester'
        person.age = 100

        self.assertEqual(person.name, 'Tester')
        self.assertEqual(person.age, 100)

    def test_getting_converted_fields(self):
        person = PersonModel()

        person.name = 735734
        person.age = '100'

        self.assertEqual(person.name, '735734')
        self.assertEqual(person.age, 100)

    def test_get_and_set_non_fields(self):
        person = PersonModel()

        person.x = 735734
        person.y = '100'

        self.assertEqual(person.x, 735734)
        self.assertEqual(person.y, '100')

    def test_getting_deleted_defaults(self):
        class PersonModelWithDefaults(Model):
            name = String(default='default_name')
            age = Integer(default=2017)

        person = PersonModelWithDefaults()

        # delete attributes because the constructor also inserts the defaults
        del person.name
        del person.age

        self.assertEqual(person.name, 'default_name')
        self.assertEqual(person.age, 2017)

    def test_validation(self):
        person = PersonModel(dict(name='Tester', age={}))

        with self.assertRaises(ValidationError):
            person.validate()

        person = PersonModel(dict(name='Tester', age='string'))

        with self.assertRaises(ValidationError):
            person.validate()

        person = PersonModel(dict(name='Tester', age=1))

        person.validate()

    def test_dump(self):
        person = PersonModel(dict(name='Tester', age=100))

        data, errors = person.dump()
        self.assertEqual(data, {
            'name': 'Tester',
            'age': 100
        })

        self.assertEqual(len(errors), 0)

        person = PersonModel(dict(name='Tester'))

        data, errors = person.dump()

        self.assertEqual(data, {
            'name': 'Tester'
        })

        self.assertEqual(len(errors), 0)

    def test_dumps(self):
        import json

        person = PersonModel(dict(name='Tester', age=100))

        data_string, errors = person.dumps()

        self.assertEqual(json.loads(data_string), {
            'name': 'Tester',
            'age': 100
        })

    def test_invalid_constructor_argument(self):
        with self.assertRaises(ValueError):
            PersonModel([])

    def test_model_methods(self):
        person = PersonModel(dict(name='Tester', age=100))

        self.assertEqual(str(person), 'Tester, 100')

    def test_inheritance(self):
        person = ParentModel(dict(name='Tester', age=100, num_children=1))

        self.assertIsNotNone(ParentSchema._declared_fields['name'])
        self.assertIsNotNone(person._schema_class._declared_fields['name'])

        self.assertEqual(person.name, 'Tester')
        self.assertEqual(person.age, 100)
        self.assertEqual(person.num_children, 1)

        person.validate()

        person = ParentModel(dict(num_children=1))

        self.assertIsNotNone(person._schema_class._declared_fields['name'])

        with self.assertRaises(ValidationError):  # missing name and age fields
            person.validate()

    def test_schema_options(self):
        with self.assertRaises(ValidationError):
            person = PersonModel()
            person.validate()

        class PersonWithMetaModel(Model):
            class Meta:
                strict = False

            name = String(required=True)
            age = Integer(required=True)

        person = PersonWithMetaModel(age=100)
        errors = person.validate()

        self.assertIsNotNone(errors['name'])
        with self.assertRaises(KeyError):
            errors['age']

    def test_strict_constructor(self):
        class PersonWithStrictConstructorModel(Model):
            class Meta:
                strict_constructor = True

            name = String(required=True)
            age = Integer(required=True)

        with self.assertRaises(ValidationError):
            person = PersonWithStrictConstructorModel()

    def test_defaults(self):
        class PersonWithDefaults(Model):
            name = String(default='Anonymous')
            age = Integer(default=0)

        person = PersonWithDefaults()

        self.assertEqual(person.name, 'Anonymous')
        self.assertEqual(person.age, 0)

        class PersonWithDefaults(Model):
            class Meta:
                strict_constructor = True

            name = String(required=True, default='Anonymous')
            age = Integer(required=True, default=0)

        # check that strict constructor doesn't fail
        person = PersonWithDefaults()

        # check that validation doesn't fail
        person.validate()

        self.assertEqual(person.name, 'Anonymous')
        self.assertEqual(person.age, 0)
