from marshmallow.schema import Schema, SchemaMeta
from compat import with_metaclass


class ModelMeta(type):
    def __new__(mcs, name, bases, attrs):
        model_class = super(ModelMeta, mcs).__new__(mcs, name, bases, attrs)

        _schema = SchemaMeta('%sSchema' % name, (Schema,), attrs)

        model_class._schema = _schema

        return model_class


class Model(with_metaclass(ModelMeta, object)):
    def __init__(self, raw_data=None, **kwargs):
        if not isinstance(raw_data, (dict, type(None))):
            raise ValueError('%s constructor accepts dictionary or kwargs.')

        self.__dict__ = raw_data or kwargs

    def validate(self):
        return self._schema(strict=True).validate(self.__dict__)
