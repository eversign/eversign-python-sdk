from schematics.types import StringType, TimestampType, IntType, DictType
from schematics.models import Model

from .utils import BaseObject


class Log(BaseObject):

    def __init__(self, **kwargs):
        kwargs = self.clear_kwargs(kwargs)
        self.__dict__['_model'] = LogModel(kwargs)
        self._model.validate()

    def validate(self):
        self._model.validate()


class LogModel(Model):
    event = StringType()
    signer = IntType()
    timestamp = TimestampType()

    class Options:
        serialize_when_none = False
