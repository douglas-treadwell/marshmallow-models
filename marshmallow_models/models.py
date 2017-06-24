from collections import Mapping
from copy import deepcopy

from marshmallow import missing
from marshmallow.schema import Schema, SchemaMeta
from marshmallow.fields import FieldABC, Nested
from compat import with_metaclass


def is_model_attribute(attr_name, attr):
    return not isinstance(attr, FieldABC)


def is_schema_attribute(attr_name, attr):
    # Meta is both a model and schema attribute
    return isinstance(attr, FieldABC) or attr_name == 'Meta'


class ModelABC(object):
    """ Exists so ModelMeta can check isinstance(_, ModelABC) """
    pass


class ModelMeta(type):
    # noinspection PyInitNewSignature
    def __new__(mcs, name, bases, attrs):
        model_attrs = {attr_name: attr
                       for attr_name, attr in attrs.items()
                       if is_model_attribute(attr_name, attr)}

        model_class = super(ModelMeta, mcs).__new__(mcs, name, bases, model_attrs)

        schema_base = getattr(model_class, '_schema_class', Schema)

        schema_attrs = {attr_name: attr
                        for attr_name, attr in attrs.items()
                        if is_schema_attribute(attr_name, attr)}

        for attr_name, attr in attrs.items():
            try:
                if issubclass(attr, ModelABC):
                    schema_attrs[attr_name] = Nested(attr._schema_class)
            except TypeError:
                pass

        _schema_class = SchemaMeta('%sSchema' % name, (schema_base,), schema_attrs)

        model_class._schema_class = _schema_class

        return model_class


class Model(with_metaclass(ModelMeta, ModelABC)):
    _default_schema_config = dict(
        strict=True
    )

    class Meta:
        # strict is not set here because if it is, it cannot be overridden
        pass

    def __init__(self, _raw_data=None, **kwargs):
        super(Model, self).__init__()

        if not isinstance(_raw_data, (dict, type(None))):
            raise ValueError('%s constructor accepts dictionary or kwargs.'
                             % self.__class__.__name__)

        strict_constructor = \
            hasattr(self, 'Meta') and \
            getattr(self.Meta, 'strict_constructor', False)

        constructor_schema = self._schema_class(strict=strict_constructor)

        input_ = _raw_data or kwargs
        input_ = input_.copy()  # don't modify the input data

        # handle case where user passes in some Models in the dict

        input_.update({
            key: deepcopy(value.__dict__)
            for key, value in input_.items()
            if isinstance(value, ModelABC)
        })

        self.__dict__.update(constructor_schema.load(input_).data)

        # TODO: reverse this loop, for keys in __class__ rather than input_

        for key, value in input_.items():
            try:
                if isinstance(value, Mapping):
                    # noinspection PyPep8Naming
                    ModelClass = getattr(self.__class__, key, None)

                    if not ModelClass:
                        continue

                    self.__dict__[key] = ModelClass(value)
            except TypeError:
                pass

        self._schema = self._schema_class(strict=self._is_strict)

    def __setattr__(self, key, value):
        if not hasattr(self, '_schema'):
            return super(Model, self).__setattr__(key, value)

        attr = self._schema.declared_fields.get(key, None)

        if isinstance(attr, FieldABC) and not isinstance(attr, Nested):
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
                default_value = attr.serialize('temp', {})

                if default_value is missing:
                    raise outer_error

                setattr(self, key, default_value)
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
        # dump() will convert nested objects into dicts
        # so we can pass the nested dicts into validate()
        # (dump() itself doesn't validate)

        data, errors = self._schema.dump(self.__dict__)

        return self._schema.validate(data)

    def dump(self):
        return self._schema.dump(self.__dict__)

    def dumps(self):
        return self._schema.dumps(self.__dict__)


# noinspection PyPep8Naming
def NestedModel(model):
    # currently a no-op, but makes nested model field declaration looking
    # similar to other field declarations, and provides a place to wrap
    # or modify the passed model in the future if needed
    return model
