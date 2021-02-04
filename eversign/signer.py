from schematics.types import StringType, IntType, EmailType, TimestampType
from schematics.models import Model

from .utils import BaseObject, BoolIntType


class Signer(BaseObject):
    validate_on_change = False

    def __init__(self, id=None, name=None, email=None, language=None, **kwargs):
        kwargs['id'] = id
        kwargs['name'] = name
        kwargs['email'] = email
        kwargs['language'] = language

        kwargs = self.clear_kwargs(kwargs)

        self.__dict__['_model'] = SignerModel(kwargs, strict=False)
        self._model.validate()


class SignerModel(Model):

    id = IntType()
    name = StringType()
    email = EmailType()
    role = StringType()
    order = IntType()
    pin = StringType()
    message = StringType()
    signed = BoolIntType()
    signed_timestamp = TimestampType()
    required = BoolIntType()
    declined = BoolIntType()
    sent = BoolIntType()
    viewed = BoolIntType()
    status = StringType()
    embedded_signing_url = StringType()
    deliver_email = BoolIntType()
    language = StringType()

    class Options:
        serialize_when_none = False
