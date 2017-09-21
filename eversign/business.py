from schematics.types import StringType, TimestampType, IntType
from schematics.models import Model

from .utils import BaseObject, BoolIntType, RangedIntType


class Business(BaseObject):

    def __init__(self, **kwargs):
        kwargs = self.clear_kwargs(kwargs)
        self.__dict__['_model'] = BusinessModel(kwargs)
        self._model.validate()

    def validate(self):
        self._model.validate()


class BusinessModel(Model):
    business_id = StringType()
    business_status = RangedIntType(min_value=1, max_value=2)
    business_identifier = StringType()
    business_name = StringType()
    creation_time_stamp = TimestampType()
    business_connection_id = IntType()
    is_primary = BoolIntType()

    class Options:
        serialize_when_none = False
