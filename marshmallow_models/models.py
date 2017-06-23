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

        _schema_class = SchemaMeta('%sSchema' % name, (schema_base,), schema_attrs)

        model_class._schema_class = _schema_class

        return model_class


class Model(with_metaclass(ModelMeta, object)):
    _default_schema_config = dict(
        strict=True
    )

    class Meta:
        # strict is not set here because if it is, it cannot be overridden
        pass

    def __init__(self, _raw_data=None, **kwargs):
        super(Model, self).__init__()

        if not isinstance(_raw_data, (dict, type(None))):
            raise ValueError('%s constructor accepts dictionary or kwargs.')

        strict_constructor = \
            hasattr(self, 'Meta') and \
            getattr(self.Meta, 'strict_constructor', False)

        constructor_schema = self._schema_class(strict=strict_constructor)

        input_ = _raw_data or kwargs

        self.__dict__ = constructor_schema.load(input_).data

        self._schema = self._schema_class(strict=self._is_strict)

    def __setattr__(self, key, value):
        if not hasattr(self, '_schema'):
            return super(Model, self).__setattr__(key, value)

        attr = self._schema.declared_fields.get(key, None)

        if isinstance(attr, FieldABC):
            # create a temporary structure to serialize the value from
            serialized_value = attr.serialize('temp', {'temp': value})
            return super(Model, self).__setattr__(key, serialized_value)
        else:
            return super(Model, self).__setattr__(key, value)

    def __getattribute__(self, key):
        try:
            return super(Model, self).__getattribute__(key)
        except AttributeError as outer_error:
            try:
                _schema = super(Model, self).__getattribute__('_schema')
            except AttributeError:
                raise outer_error

            attr = _schema.declared_fields.get(key, None)

            if isinstance(attr, FieldABC):
                setattr(self, key, attr.serialize('temp', {}))
                return super(Model, self).__getattribute__(key)
            else:
                raise outer_error

    @property
    def _is_strict(self):
        try:
            return self.Meta.strict
        except AttributeError:
            return self._default_schema_config['strict']

    def validate(self):
        return self._schema.validate(self.__dict__)

    def dump(self):
        return self._schema.dump(self.__dict__)

    def dumps(self):
        return self._schema.dumps(self.__dict__)
