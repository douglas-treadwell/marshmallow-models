from unittest import TestCase
from marshmallow import Schema
from marshmallow_models import Model, NestedModel
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

    def test_getting_defaults_after_deletion(self):
        class PersonModelWithDefaults(Model):
            name = String(default='default_name', missing='missing_name')
            age = Integer(default=2017, missing=7102)

        person = PersonModelWithDefaults()

        self.assertEqual(person.name, 'missing_name')
        self.assertEqual(person.age, 7102)

        # delete the attributes with missing= that the constructor inserted

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

    def test_non_strict_constructor(self):
        class PersonWithStrictConstructorModel(Model):
            class Meta:
                strict_constructor = False

            name = String(required=True)
            age = Integer(required=True)

        person = PersonWithStrictConstructorModel()

        # constructor correctly didn't raise an exception
        self.assertIsNotNone(person)

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

        self.assertNotIn('name', person.__dict__)
        self.assertNotIn('age', person.__dict__)

        self.assertEqual(person.name, 'Anonymous')
        self.assertEqual(person.age, 0)

        class PersonWithDefaults(Model):
            class Meta:
                strict_constructor = True

            name = String(required=True, default='Anonymous')
            age = Integer(required=True, default=0)

        # check that strict constructor fails
        with self.assertRaises(ValidationError):
            person = PersonWithDefaults()

        # check that validation doesn't fail
        person.validate()

        self.assertEqual(person.name, 'Anonymous')
        self.assertEqual(person.age, 0)

    def test_missing(self):
        class PersonWithMissing(Model):
            name = String(missing='Anonymous')
            age = Integer(missing=0)

        person = PersonWithMissing()

        self.assertEqual(person.name, 'Anonymous')
        self.assertEqual(person.age, 0)

        class PersonWithMissing(Model):
            class Meta:
                strict_constructor = True

            name = String(required=True, missing='Anonymous')
            age = Integer(required=True, missing=0)

        # check that strict constructor doesn't fail
        person = PersonWithMissing()

        # check that validation doesn't fail
        person.validate()

        self.assertEqual(person.name, 'Anonymous')
        self.assertEqual(person.age, 0)

    def test_constructor_nested_models(self):
        class ParentModel(PersonModel):
            child = NestedModel(PersonModel)

        parent1 = ParentModel(name='Tester', age=40, child=dict(name='Child1', age=10))
        parent2 = ParentModel(name='Tester', age=40, child=dict(name='Child2', age=10))

        self.assertEqual(parent1.child.name, 'Child1')
        self.assertEqual(parent2.child.name, 'Child2')

        parent1.child.validate()
        parent1.validate()

    def test_set_nested_model_attributes(self):
        class ParentModel(PersonModel):
            child = NestedModel(PersonModel)

        parent = ParentModel(name='Tester', age=40, child=dict(name='Child', age=10))

        self.assertEqual(parent.child.name, 'Child')

        parent.child.name = 'Kid'

        self.assertEqual(parent.child.name, 'Kid')

        self.assertEqual(parent.dump().data['child']['name'], 'Kid')

        parent.child.validate()
        parent.validate()

    def test_assign_nested_model(self):
        class ParentModel(PersonModel):
            child = NestedModel(PersonModel)

        parent = ParentModel(name='Tester', age=40, child=dict(name='Child', age=10))

        child = PersonModel(name='Kiddo', age=11)

        parent.child = child

        self.assertEqual(parent.dump().data['child']['name'], 'Kiddo')

        parent.child.validate()
        parent.validate()

    def test_delete_nested_model_attributes(self):
        class ParentModel(PersonModel):
            child = NestedModel(PersonModel)

        parent = ParentModel(name='Tester', age=40, child=dict(name='Child', age=10))

        del parent.child.name

        with self.assertRaises(AttributeError):
            parent.child.name = parent.child.name  # rhs raises exception

        with self.assertRaises(ValidationError):
            parent.child.validate()

        with self.assertRaises(ValidationError):
            parent.validate()

        parent.child.name = 'Kid'

        self.assertEqual(parent.child.name, 'Kid')
        parent.child.validate()
        parent.validate()
