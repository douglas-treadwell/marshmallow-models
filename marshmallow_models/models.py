from collections import Mapping
from copy import deepcopy

from marshmallow.schema import Schema, SchemaMeta
from marshmallow.fields import FieldABC, Nested
from compat import with_metaclass

from .base import ModelABC
from .field_descriptor import FieldDescriptor
from .nested_model_descriptor import NestedModelDescriptor


def wrap_models_and_fields(attr, attr_name):
    try:
        if issubclass(attr, ModelABC):
            return NestedModelDescriptor(attr_name, attr)
    except TypeError:
        pass

    if isinstance(attr, FieldABC):
        return FieldDescriptor(attr_name)
    else:
        return attr


def is_schema_attribute(attr_name, attr):
    # Meta is both a model and schema attribute
    return isinstance(attr, FieldABC) or attr_name == 'Meta'


class ModelMeta(type):
    # noinspection PyInitNewSignature
    def __new__(mcs, name, bases, attrs):
        model_attrs = {attr_name: wrap_models_and_fields(attr, attr_name)
                       for attr_name, attr in attrs.items()}

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

        self._data = {}

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

        # noinspection PyProtectedMember
        input_.update({
            key: deepcopy(value._data)
            for key, value in input_.items()
            if isinstance(value, ModelABC)
        })

        self._data.update(constructor_schema.load(input_).data)

        # TODO: reverse this loop, for keys in __class__ rather than input_

        for key, value in input_.items():
            try:
                if isinstance(value, Mapping):
                    # noinspection PyPep8Naming
                    ModelClass = getattr(self.__class__, key, None)

                    if not ModelClass:
                        continue

                    self._data[key] = ModelClass(value)
            except TypeError:
                pass

        self._schema = self._schema_class(strict=self._is_strict)

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

        data, errors = self._schema.dump(self._data)

        return self._schema.validate(data)

    def dump(self):
        return self._schema.dump(self._data)

    def dumps(self):
        return self._schema.dumps(self._data)


# noinspection PyPep8Naming
def NestedModel(model):
    # currently a no-op, but makes nested model field declaration looking
    # similar to other field declarations, and provides a place to wrap
    # or modify the passed model in the future if needed
    return model
