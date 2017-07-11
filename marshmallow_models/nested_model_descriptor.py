# noinspection PyProtectedMember
class NestedModelDescriptor(object):
    def __init__(self, field_name, model):
        self.field_name = field_name
        self.model = model

    def __get__(self, model_instance, model_class):
        if model_instance is None:
            return self.model

        try:
            return model_instance._data[self.field_name]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'"
                                 % (model_instance.__class__.__name__, self.field_name))

    def __set__(self, model_instance, value):
        # TODO: raise exceptions if invalid value is set
        model_instance._data[self.field_name] = value

    def __delete__(self, model_instance):
        del model_instance._data[self.field_name]
