from schematics.types import StringType, IntType, ListType, DecimalType
from schematics.models import Model

from .utils import BaseObject, BoolIntType


class Field(BaseObject):
    validate_on_change = False
    merge_field = False
    validation = ['letters_only', 'numbers_only', 'email_address']
    fonts = ['arial', 'calibri', 'courier_new',
             'helvetica', 'georgia', 'times_new_roman']
    styles = ['B', 'U', 'I']

    def __init__(self, **kwargs):
        kwargs = self.clear_kwargs(kwargs)

        self.__dict__['_model'] = FieldModel(kwargs, strict=False)
        self.__dict__['validate_on_change'] = False

    def validate(self):
        self._model.validate()
        self.validate_validation()
        self.validate_textfields()

    def validate_textfields(self):
        if self.text_font and self.text_font not in self.fonts:
            raise Exception
        if self.text_style:
            for char in self.text_style:
                if not char in self.styles:
                    raise Exception

    def validate_validation(self):
        if self.validation_type:
            if self.validation_type in self.validation:
                return True
            else:
                raise Exception
        else:
            return True


class FieldModel(Model):

    type = StringType(required=True)
    merge = BoolIntType()
    x = DecimalType()
    y = DecimalType()
    width = StringType()
    height = StringType()
    page = StringType()
    signer = StringType()
    name = StringType()
    identifier = StringType()
    required = BoolIntType()
    readonly = BoolIntType()
    validation_type = StringType()
    text_style = StringType()
    text_font = StringType()
    text_size = IntType()
    text_color = StringType()
    value = StringType()
    options = ListType(StringType)
    group = StringType()

    class Options:
        serialize_when_none = False


class SignatureField(Field):

    def __init__(self, **kwargs):
        kwargs['type'] = 'signature'
        super(self.__class__, self).__init__(**kwargs)


class InitialsField(Field):

    def __init__(self, **kwargs):
        kwargs['type'] = 'initials'
        super(self.__class__, self).__init__(**kwargs)


class DateSignedField(Field):

    def __init__(self, **kwargs):
        kwargs['type'] = 'date_signed'
        super(self.__class__, self).__init__(**kwargs)


class NoteField(Field):
    merge_field = True

    def __init__(self, **kwargs):
        kwargs['type'] = 'note'
        super(self.__class__, self).__init__(**kwargs)


class TextField(Field):
    merge_field = True

    def __init__(self, **kwargs):
        kwargs['type'] = 'text'
        super(self.__class__, self).__init__(**kwargs)


class CheckboxField(Field):
    merge_field = True

    def __init__(self, **kwargs):
        kwargs['type'] = 'checkbox'
        super(self.__class__, self).__init__(**kwargs)


class RadioField(Field):
    merge_field = True

    def __init__(self, **kwargs):
        kwargs['type'] = 'radio'
        super(self.__class__, self).__init__(**kwargs)


class DropdownField(Field):
    merge_field = True

    def __init__(self, **kwargs):
        kwargs['type'] = 'dropdown'
        super(self.__class__, self).__init__(**kwargs)


class AttachmentField(Field):

    def __init__(self, **kwargs):
        kwargs['type'] = 'attachment'
        super(self.__class__, self).__init__(**kwargs)
