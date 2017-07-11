from marshmallow.fields import Nested
from marshmallow import missing


# noinspection PyProtectedMember
class FieldDescriptor(object):
    def __init__(self, field_name):
        self.field_name = field_name

    def _get_class_field(self, model_class):
        try:
            return model_class._schema_class._declared_fields[self.field_name]
        except KeyError:
            # convert KeyError into a more meaningful AttributeError
            raise AttributeError("type object '%s' has no attribute '%s'"
                                 % (model_class.__name__, self.field_name))

    def _get_instance_field(self, model_instance):
        return model_instance._schema.declared_fields[self.field_name]

    def _set_instance_value(self, model_instance, value):
        model_instance._data[self.field_name] = value

    def _get_instance_value(self, model_instance):
        return model_instance._data[self.field_name]

    def __get__(self, model_instance, model_class):
        """ Equivalent to serialization. """

        if model_instance is None:
            # simulate that the Field is an attribute of the Model
            return self._get_class_field(model_class)

        try:
            return self._get_instance_value(model_instance)
        except KeyError:
            schema_field = self._get_instance_field(model_instance)

            default_value = schema_field.serialize('temp', {})

            if default_value is missing:
                raise AttributeError("'%s' object has no attribute '%s'"
                                     % (model_instance.__class__.__name__, self.field_name))

            self._set_instance_value(model_instance, default_value)
            return default_value

    def __set__(self, model_instance, value):
        """ Equivalent to deserialization. """

        schema_field = self._get_instance_field(model_instance)

        if not isinstance(schema_field, Nested):
            # create a temporary structure to serialize the value from
            serialized_value = schema_field.serialize('temp', {'temp': value})
            self._set_instance_value(model_instance, serialized_value)
        else:
            self._set_instance_value(model_instance, value)

    def __delete__(self, model_instance):
        del model_instance._data[self.field_name]
