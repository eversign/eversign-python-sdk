from schematics.types import StringType, IntType
from schematics.models import Model

from .utils import BaseObject


class File(BaseObject):
    validate_on_change = False

    def __init__(self, name=None, **kwargs):
        self.__dict__['_model'] = FileModel(kwargs, strict=False)
        self.name = name
        self._model.validate()

    def validate(self):
        self._model.validate()
        if len([x for x in self.to_primitive().keys() if x.startswith('file_')]) > 1:
            raise Exception('Please provide only one file option')


class FileModel(Model):
    name = StringType(required=True)
    file_id = StringType()
    file_url = StringType()
    file_base64 = StringType()
    pages = IntType()

    class Options:
        serialize_when_none = False
