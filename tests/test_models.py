from unittest import TestCase
from marshmallow_models import Model
from marshmallow.fields import String, Integer
from marshmallow.exceptions import ValidationError


class PersonModel(Model):
    name = String(required=True)
    age = Integer(required=True)


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
