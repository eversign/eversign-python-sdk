from schematics.types import NumberType
from schematics.exceptions import DataError
import six


class EversignException(Exception):

    def __init__(self, code, type, info):
        self.code = code
        self.type = type
        self.info = info


class BoolIntType(NumberType):

    def __init__(self, **kwargs):
        kwargs['min_value'] = 0
        kwargs['max_value'] = 1
        super(self.__class__, self).__init__(**kwargs)

        self.native_type = int
        self.number_type = 'Int'
        self.number_class = int


class RangedIntType(NumberType):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

        self.native_type = int
        self.number_type = 'Int'
        self.number_class = int


class BaseObject(object):
    _model = dict()
    validate_on_change = True

    def clear_kwargs(self, kwargs):
        for kw in kwargs.keys():
            if isinstance(kwargs[kw], six.string_types) and not kwargs[kw]:
                kwargs[kw] = None
        return kwargs

    def __getattr__(self, item):
        return self._model[item]

    def __getitem__(self, item):
        return self._model[item]

    def __setitem__(self, key, item):
        self.set(key, item)

    def __setattr__(self, key, value):
        self.set(key, value)

    def __repr__(self):
        return str(self._model.to_primitive())

    @property
    def _model(self):
        return self.__dict__['_model']

    def validate(self):
        self._model.validate()

    def to_primitive(self):
        return self._model.to_primitive()

    def set(self, key, value):
        try:
            old = self._model[key]
            self._model[key] = value
            if self.validate_on_change:
                self.validate()
        except DataError as error:
            self._model[key] = old
            raise error
