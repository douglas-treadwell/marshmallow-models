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
        if 'Options' in attrs:  # support Options alias for Meta
            attrs['Meta'] = attrs['Options']

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
        if not isinstance(_raw_data, (dict, type(None))):
            raise ValueError('%s constructor accepts dictionary or kwargs.')

        strict_constructor = \
            hasattr(self, 'Meta') and \
            getattr(self.Meta, 'strict_constructor', False)

        constructor_schema = self._schema_class(strict=strict_constructor)

        input_ = _raw_data or kwargs

        self.__dict__ = constructor_schema.dump(input_).data

        if strict_constructor:
            constructor_schema.validate(self.__dict__)

        self._schema = self._schema_class(strict=self._is_strict)

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
