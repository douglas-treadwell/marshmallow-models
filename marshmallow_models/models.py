from marshmallow.schema import Schema, SchemaMeta
from marshmallow.fields import FieldABC
from compat import with_metaclass


def is_schema_attribute(attr):
    return isinstance(attr, FieldABC)


class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        model_attrs = {attr_name: attr
                       for attr_name, attr in attrs.items()
                       if not is_schema_attribute(attr)}

        model_class = super(ModelMeta, mcs).__new__(mcs, name, bases, model_attrs)

        schema_base = getattr(model_class, '_schema_class', Schema)

        schema_attrs = {attr_name: attr
                        for attr_name, attr in attrs.items()
                        if is_schema_attribute(attr)}

        _schema_class = SchemaMeta('%sSchema' % name, (schema_base,), schema_attrs)

        model_class._schema_class = _schema_class

        return model_class


class Model(with_metaclass(ModelMeta, object)):
    def __init__(self, _raw_data=None, **kwargs):
        if not isinstance(_raw_data, (dict, type(None))):
            raise ValueError('%s constructor accepts dictionary or kwargs.')

        self.__dict__ = _raw_data or kwargs

    @property
    def _instance_schema(self):
        if not hasattr(self, '_schema'):
            self._schema = self._schema_class(strict=True)

        return self._schema

    def validate(self):
        return self._instance_schema.validate(self.__dict__)
