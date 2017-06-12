from marshmallow.schema import Schema, SchemaMeta
from marshmallow.fields import FieldABC
from compat import with_metaclass


def is_model_attribute(attr_name, attr):
    return not isinstance(attr, FieldABC)


def is_schema_attribute(attr_name, attr):
    # Meta or Options are both model and schema attributes
    return isinstance(attr, FieldABC) or attr_name in ('Meta', 'Options')


class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        model_attrs = {attr_name: attr
                       for attr_name, attr in attrs.items()
                       if is_model_attribute(attr_name, attr)}

        model_class = super(ModelMeta, mcs).__new__(mcs, name, bases, model_attrs)

        schema_base = getattr(model_class, '_schema_class', Schema)

        schema_attrs = {attr_name: attr
                        for attr_name, attr in attrs.items()
                        if is_schema_attribute(attr_name, attr)}

        if 'Options' in schema_attrs:  # support Options alias for Meta
            schema_attrs['Meta'] = schema_attrs['Options']
            del schema_attrs['Options']

        _schema_class = SchemaMeta('%sSchema' % name, (schema_base,), schema_attrs)

        model_class._schema_class = _schema_class

        return model_class


class Model(with_metaclass(ModelMeta, object)):
    class Meta:  # default options
        strict = True

    def __init__(self, _raw_data=None, **kwargs):
        if not isinstance(_raw_data, (dict, type(None))):
            raise ValueError('%s constructor accepts dictionary or kwargs.')

        self.__dict__ = _raw_data or kwargs

    @property
    def _instance_schema(self):
        if not hasattr(self, '_schema'):
            self._schema = self._schema_class()

        return self._schema

    def validate(self):
        return self._instance_schema.validate(self.__dict__)
