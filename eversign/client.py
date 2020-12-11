import eversign
import requests
import json
import requests.exceptions
import six
import os.path
import os
import errno
import logging

from pprint import pprint

from .document import Document, Template
from .business import Business
from .utils import EversignException


class Client(object):
    access_key = None
    headers = {}
    businesses = None
    business_id = None
    debug = False

    def __init__(self, access_key=None, business_id=None):

        self.headers['User-Agent'] = 'Eversign_Python_SDK'

        if access_key:
            if access_key.startswith('Bearer '):
                self.set_oauth_access_token(access_key)
            else:
                self.access_key = access_key

        self.api_base = eversign.api_base
        self.oauth_base = eversign.oauth_base

        if eversign.debug:
            self.debug = True
            logging.basicConfig(level=logging.DEBUG,
                                format='%(asctime)s %(message)s')

        if business_id:
            self.business_id = business_id
        elif access_key:
            self.fetch_businesses()

    def set_oauth_access_token(self, oauthtoken):
        if oauthtoken.startswith('Bearer '):
            self.headers['Authorization'] = oauthtoken
        else:
            self.headers['Authorization'] = 'Bearer ' + oauthtoken

        self.fetch_businesses()

    def generate_oauth_authorization_url(self, options):
        self._check_arguments(['client_id', 'state'], options)

        return eversign.oauth_base + '/authorize?client_id=' + options['client_id'] + '&state=' + options['state']

    def request_oauth_token(self, options):
        self._check_arguments(
            ['client_id', 'client_secret', 'code', 'state'], options)

        r = requests.post(eversign.oauth_base + '/token', data=options)
        if r.status_code == 200:
            response_obj = json.loads(r.text)

            if "error" in response_obj:
                raise Exception(response_obj['message'])

            if response_obj['success']:
                return response_obj['access_token']

        raise Exception('no success')

    def set_selected_business(self, business):
        self.business_id = business.business_id

    def set_selected_business_by_id(self, business_id):
        self.business_id = business_id

    def get_businesses(self):
        return self.businesses

    def fetch_businesses(self):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-businesses

        A list of existing businesses on your Eversign account.
        Sets the primary business on the client to the one set on your account.

        Returns:
            eversign.Business object for success, raises Exception for failure.

        """
        response = self._request('/business', return_type=Business)

        if response:
            self.businesses = response
            for business in response:
                if business.is_primary:
                    self.business_id = business.business_id

        return response

    def create_document(self, document):
        """
        Documentation: https://eversign.com/api/documentation/methods#create-document

        Creates a prepared document.

        Args:
            document (eversign.Document): Document to be created.

        Returns:
            eversign.Document object for success, raises Exception for failure.

        """
        for file in document.files:
            if file.file_url:
                if not os.path.exists(file.file_url):
                    raise FileNotFoundError(
                        errno.ENOENT, os.strerror(errno.ENOENT), file.file_url)
                response = self.upload_file(file.file_url)
                file.file_url = None
                file.file_id = response['file_id']

        return self._request('/document', method="POST", data=document.to_primitive(),
                             return_type=Document)

    def create_document_from_template(self, template):
        """
        Documentation: https://eversign.com/api/documentation/methods#use-template

        Creates a prepared template.

        Args:
            template (eversign.Document): Document to be created.

        Returns:
            eversign.Document object for success, raises Exception for failure.

        """
        if type(template) is Template:
            template.validate()
            primitive_document = template.to_primitive()

            self._role_needed(primitive_document['signers'], 'signer')
            self._role_needed(primitive_document['recipients'], 'recipient')

            data = {
                'template_id': template.document_hash or template.template_id,
                'sandbox': template.sandbox,
                'title': template.title,
                'message': template.title,
                'redirect': template.redirect,
                'redirect_decline': template.redirect_decline,
                'client': template.client if not "eversign_portal" else "python-sdk",
                'expires': template.expires,
                'signers': primitive_document['signers'],
                'recipients': primitive_document['recipients'],
                'fields': template._get_fields_for_template(),
                'embedded_signing_enabled': template.embedded_signing_enabled
            }

            return self._request('/document', method='POST', data=data, return_type=Document)
        else:
            raise Exception

    def get_document_by_hash(self, document_hash=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#get-document-template

        Gets a single document.

        Args:
            document_hash (str): If a document_hash is specified, it will override the document argument.

        Returns:
            eversign.Document object for success, raises Exception for failure.

        """
        return self._request('/document', params={'document_hash': document_hash},
                             return_type=Document)

    def get_all_documents(self):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-documents

        Retrieves the documents from eversign API

        Returns:
            List of eversign.Document object for success, raises Exception for failure.

        """
        return self._get_documents('all')

    def get_completed_documents(self):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-documents

        Retrieves all completed documents from eversign API

        Returns:
            List of eversign.Document object for success, raises Exception for failure.

        """
        return self._get_documents('completed')

    def get_draft_documents(self):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-documents

        Retrieves all draft documents from eversign API

        Returns:
            List of eversign.Document object for success, raises Exception for failure.

        """
        return self._get_documents('draft')

    def get_canceled_documents(self):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-documents

        Retrieves all canceled documents from eversign API

        Returns:
            List of eversign.Document object for success, raises Exception for failure.

        """
        return self._get_documents('canceled')

    def get_action_required_documents(self):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-documents

        Returns all Documents for the Client which require Actions

        Returns:
            List of eversign.Document object for success, raises Exception for failure.

        """
        return self._get_documents('my_action_required')

    def get_waiting_for_others_documents(self):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-documents

        Returns all Documents for the Client which are waiting on responses

        Returns:
            List of eversign.Document object for success, raises Exception for failure.

        """
        return self._get_documents('waiting_for_others')

    def get_templates(self):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-documents

        Returns a list of Documents which are set to be Templates

        Returns:
            List of eversign.Document object for success, raises Exception for failure.

        """
        return self._get_documents('templates')

    def get_archived_templates(self):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-documents

        Returns a list of Documents which are set to be Templates

        Returns:
            List of eversign.Document object for success, raises Exception for failure.

        """
        return self._get_documents('templates_archived')

    def get_draft_templates(self):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-documents

        Returns a list of Documents which are set to be Templates

        Returns:
            List of eversign.Document object for success, raises Exception for failure.

        """
        return self._get_documents('template_drafts')

    def send_reminder_for_document(self, document, signer):
        """
        Documentation: https://eversign.com/api/documentation/methods#send-reminder

        Sends a reminder email to the specified document and signer.

        Args:
            document (eversign.Document)
            signer (eversign.Signer)

        Returns:
            JSON Response from the API

        """
        return self._request('/send_reminder', method="POST", data={
            'document_hash': self._get_document_hash(document),
            'signer_id': signer.id
        })

    def cancel_document(self, document):
        """
        Documentation: https://eversign.com/api/documentation/methods#cancel-document

        Cancels a document.

        Args:
            document (eversign.Document)

        Returns:
            True for success, raises exception on failure.

        """
        return self.delete_document(document, 1)

    def delete_document(self, document, cancel=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#delete-document

        Deletes a document, only drafts and cancelled documents can be deleted.

        Args:
            document (eversign.Document)
            cancel (bool, optional)

        Returns:
            True for success, raises exception on failure.

        """
        params = dict()
        if type(document) is Document:
            if cancel or document.is_cancelled or document.is_draft:
                params['document_hash'] = self._get_document_hash(document)
            else:
                raise Exception(
                    'Only drafts and cancelled documents can be deleted')
        else:
            raise Exception('Please provide a document')

        if cancel:
            params['cancel'] = cancel

        return self._request('/document', 'DELETE', params=params)

    def download_final_document_to_path(self, document, path, audit_trail=1):
        """
        Documentation: https://eversign.com/api/documentation/methods#download-final-pdf

        Downloads the final signed PDF to the specified path.

        Args:
            document (eversign.Document)
            path (str): Local path on the file system
            audit_trail (int, optional): Defaults to 1.

        Returns:
            True for success, raises exception on failure.
        """
        return self._download('/download_final_document', path, params={
            'business_id': self.business_id,
            'document_hash': self._get_document_hash(document),
            'audit_trail': audit_trail
        })

    def download_raw_document_to_path(self, document, path):
        """
        Documentation: https://eversign.com/api/documentation/methods#download-original-pdf

        Deletes a document, only drafts and cancelled documents can be deleted.

        Args:
            document (eversign.Document)
            path (str): Local path on the file system

        Returns:
            True for success, raises exception on failure.
        """
        return self._download('/download_raw_document', path, params={
            'business_id': self.business_id,
            'document_hash': self._get_document_hash(document)
        })

    def upload_file(self, path):
        """
        Documentation: https://eversign.com/api/documentation/methods#upload-file

        Uploads a file to Eversign.

        Args:
            path (str): Local path on the file system

        Returns:
            JSON response from the API, exception on error
        """
        try:
            url = self.api_base + '/file'
            params = dict()
            params['access_key'] = self.access_key
            params['business_id'] = self.business_id

            response = requests.post(url, files={
                'upload': open(path, 'rb')
            }, params=params)

        except requests.exceptions.RequestException:
            raise
        except IOError:
            raise

        if response.status_code == 200 and 'error' not in response.text:
            return json.loads(response.text)
        else:
            raise Exception(response.text)

    def _check_arguments(self, arguments=[], options=()):
        for argument in arguments:
            if argument not in options:
                raise Exception('Please specify ' + argument)

    def _get_documents(self, type='all'):
        return_type = Document
        if type in ['templates', 'templates_archived', 'template_drafts']:
            return_type = Template

        try:
            return self._request(
                '/document',
                params={'type': type},
                return_type=return_type)
        except Exception as e:
            if e.type == 'no_result':
                return []
            else:
                raise e

    def _role_needed(self, obj, name):
        for element in obj:
            if 'role' not in element.keys() or not element['role']:
                raise Exception('A role is needed for every ' + name)

    def _download(self, url, path, params):
        try:
            import urllib.parse as uparse
            import urllib.request as urequest
        except ImportError:
            import urllib as uparse
            import urllib as urequest
        try:
            params['access_key'] = self.access_key
            url = self.api_base + url + '?' + uparse.urlencode(params)
            urequest.urlretrieve(url, path)
        except Exception:
            raise

    def _request(self, url, method="GET", params=dict(), data=None,
                 return_type=None):
        url = self.api_base + url

        if self.access_key:
            params['access_key'] = self.access_key

        params['business_id'] = self.business_id

        try:
            if method in ["GET", "DELETE"]:
                response = requests.request(
                    method, url, headers=self.headers, params=params)

            elif method in ["POST", "PUT"]:
                if self.debug:
                    logging.debug(data)
                response = requests.request(
                    method, url, headers=self.headers, params=params, json=data)

            else:
                raise Exception("Method not supported")

            response_obj = json.loads(response.text)

            if self.debug:
                logging.debug(response_obj)

            if "error" in response_obj:
                error = response_obj['error']
                code = error['code'] if 'code' in error.keys() else None
                _type = error['type'] if 'type' in error.keys() else None
                info = error['info'] if 'info' in error.keys() else None
                raise EversignException(code, _type, info)

            if return_type:
                if type(response_obj) is list:
                    lst = []
                    for element in response_obj:
                        try:
                            lst.append(self._serialize(element, return_type))
                        except Exception:
                            raise
                    return lst
                else:
                    return self._serialize(response_obj, return_type)

            if 'success' in response_obj and response_obj['success']:
                return True
            return response_obj

        except requests.exceptions.RequestException:
            raise

    def _serialize(self, object, model):
        try:
            return model(**object)
        except Exception:
            raise

    def _get_document_hash(self, document):
        if type(document) is Document:
            return document.document_hash
        elif isinstance(document, six.string_types):
            return document
        else:
            raise Exception
