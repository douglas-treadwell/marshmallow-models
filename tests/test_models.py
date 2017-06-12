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

    def test_validation(self):
        person = PersonModel(dict(name='Tester', age={}))

        with self.assertRaises(ValidationError):
            person.validate()

        person = PersonModel(dict(name='Tester', age='string'))

        with self.assertRaises(ValidationError):
            person.validate()

        person = PersonModel(dict(name='Tester', age=1))

        person.validate()

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
