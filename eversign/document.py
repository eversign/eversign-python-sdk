from schematics.models import Model
from schematics.types import StringType, TimestampType, ListType, DictType

from .utils import BoolIntType, BaseObject, RangedIntType

from .recipient import Recipient
from .file import File
from .signer import Signer
from .field import Field
from .log import Log


class Document(BaseObject):

    def __init__(self, **kwargs):

        self.__dict__['_files'] = []
        self.__dict__['_signers'] = []
        self.__dict__['_recipients'] = []
        self.__dict__['_fields'] = []
        self.__dict__['_logs'] = []

        mapping = {'files': (File, '_files'),
                   'signers': (Signer, '_signers'),
                   'fields': (Field, '_fields'),
                   'recipients': (Recipient, '_recipients'),
                   'log': (Log, '_logs')}

        for kw in mapping.keys():
            if kw in kwargs:
                self.__dict__[mapping[kw][1]] = self.from_object(
                    kw, kwargs, mapping[kw][0])
                kwargs.pop(kw, None)

        kwargs = self.clear_kwargs(kwargs)
        if 'meta' in kwargs.keys() and type(kwargs['meta']) is list:
            kwargs['meta'] = dict()

        self.__dict__['_model'] = DocumentModel(kwargs, strict=False)

    @property
    def files(self):
        return self.__dict__['_files']

    @property
    def signers(self):
        return self.__dict__['_signers']

    @property
    def recipients(self):
        return self.__dict__['_recipients']

    @property
    def fields(self):
        return self.__dict__['_fields']

    @property
    def log(self):
        return self.__dict__['_logs']

    def from_object(self, name, object, _class):
        result = []
        if name in object.keys():
            for obj in object[name]:
                if type(obj) is list:
                    lst = []
                    for element in obj:
                        lst.append(_class(**element))
                    result.append(lst)
                else:
                    result.append(_class(**obj))
        return result

    def _convert_to_primitive(self, lst):
        return [x.to_primitive() for x in lst]

    def to_primitive(self):
        model = self._model.to_primitive()

        model['files'] = self._convert_to_primitive(self.files)
        model['signers'] = self._convert_to_primitive(self.signers)
        model['recipients'] = self._convert_to_primitive(self.recipients)
        fields = []

        for field_list in self._fields:
            lst = []
            for field in field_list:
                lst.append(field.to_primitive())
            fields.append(lst)

        model['fields'] = fields
        model['logs'] = self._convert_to_primitive(self._logs)

        return model

    def __repr__(self):
        return str(self.to_primitive())

    def add_recipient(self, recipient):
        return self._add(recipient)

    def add_file(self, _file):
        return self._add(_file)

    def add_signer(self, signer):
        if not signer.id:
            signer.id = len(self.signers) + 1
        return self._add(signer)

    def add_field(self, field):
        return self.add_field_list([field])

    def add_field_list(self, field_list):
        for field in field_list:
            field.validate()
        self._fields.append(field_list)

    def _add(self, item):
        mapping = {
            Recipient: '_recipients',
            File: '_files',
            Signer: '_signers',
            Field: '_fields',
        }

        if mapping[type(item)]:
            item.validate()
            lst = getattr(self, mapping[type(item)], item)
            lst.append(item)

    def validate(self):
        self._model.validate()
        for f in ['files', 'signers', 'recipients', 'fields']:
            self._validate_list(getattr(self, f))

    def _validate_list(self, lst):
        for element in lst:
            if type(element) is list:
                self._validate_list(element)
            else:
                element.validate()

    def _get_fields_for_template(self):
        field_lst = []
        for fields in self.fields:
            if len(fields) > 0:
                for field in fields:
                    if field.merge_field:
                        if field.identifier and field.value:
                            field_lst.append({
                                'identifier': field.identifier,
                                'value': field.value
                            })
                        else:
                            raise Exception(
                                'An identifier and a value are needed for merge fields.')

        return field_lst


class Template(Document):
    pass


class DocumentModel(Model):

    document_hash = StringType()
    template_id = StringType()
    requester_email = StringType()
    title = StringType()
    subject = StringType()
    message = StringType()
    iframe = StringType()
    is_draft = BoolIntType()
    is_template = BoolIntType()
    is_completed = BoolIntType()
    is_archived = BoolIntType()
    is_deleted = BoolIntType()
    is_trashed = BoolIntType()
    is_cancelled = BoolIntType()
    embedded = BoolIntType()
    in_person = BoolIntType()
    permission = RangedIntType(min_value=0, max_value=2)
    use_signer_order = BoolIntType()
    reminders = BoolIntType()
    require_all_signers = BoolIntType()
    redirect = StringType()
    redirect_decline = StringType()
    client = StringType()
    created = TimestampType()
    expires = TimestampType()
    meta = DictType(StringType)

    class Options:
        serialize_when_none = False
