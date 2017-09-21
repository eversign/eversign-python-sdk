import eversign
import requests
import json
import requests.exceptions
import six
import os.path
import os
import errno
import logging

from .document import Document
from .business import Business
from .utils import EversignException


class Client(object):
    business_id = None
    debug = False

    def __init__(self, access_key=None, business_id=None, debug=False):

        self.access_key = access_key
        self.api_base = eversign.api_base

        if debug:
            self.debug = True
            logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')

        if business_id:
            self.business_id = business_id
        else:
            self.get_businesses()

    def get_businesses(self):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-businesses

        A list of existing businesses on your Eversign account.
        Sets the primary business on the client to the one set on your account.

        Returns:
            eversign.Business object for success, raises Exception for failure.

        """
        response = self._request('/business', return_type=Business)

        if response:
            for business in response:
                if business.is_primary:
                    self.business_id = business.business_id

        return response

    def create_document(self, document, business_id=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#create-document

        Creates a prepared document.

        Args:
            document (eversign.Document): Document to be created.
            business_id (int, optional): Defaults to the primary business_id.

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

        return self._request('/document', business_id=business_id, method="POST", data=document.to_primitive(),
                             return_type=Document)

    def create_document_from_template(self, template, business_id=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#use-template

        Creates a prepared template.

        Args:
            template (eversign.Document): Document to be created.
            business_id (int, optional): Defaults to the primary business_id.

        Returns:
            eversign.Document object for success, raises Exception for failure.

        """
        if type(template) is Document:
            template.validate()
            primitive_document = template.to_primitive()

            self._role_needed(primitive_document['signers'], 'signer')
            self._role_needed(primitive_document['recipients'], 'recipient')

            data = {
                'template_id': template.document_hash or template.template_id,
                'title': template.title,
                'message': template.title,
                'redirect': template.redirect,
                'redirect_decline': template.redirect_decline,
                'client': template.client if not "eversign_portal" else "python-sdk",
                'expires': template.expires,
                'signers': primitive_document['signers'],
                'recipients': primitive_document['recipients'],
                'fields': template._get_fields_for_template()
            }

            return self._request('/document', business_id=business_id, method='POST', data=data, return_type=Document)
        else:
            raise Exception

    def get_template(self, template_id, business_id=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#get-document-template

        Gets a single template

        Args:
            template_id (int)
            business_id (int, optional): Defaults to the primary business_id.

        Returns:
            eversign.Document object for success, raises Exception for failure.

        """
        return self._request('/document', business_id=business_id,
                             params={'document_hash': template_id},
                             return_type=Document)

    def get_document(self, document, document_hash=None, business_id=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#get-document-template

        Gets a single document.

        Args:
            document(eversign.Document)
            document_hash (str): If a document_hash is specified, it will override the document argument.
            business_id (int, optional): Defaults to the primary business_id.

        Returns:
            eversign.Document object for success, raises Exception for failure.

        """
        return self.get_template(document_hash or document.document_hash, business_id)

    def list_templates(self, type="templates", business_id=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-templates

        Lists all the templates with specified type.

        Args:
            type (str): Allowed values:
                - "templates"
                - "templates_archived"
                - "template_drafts"
                Defaults to "templates"
            business_id (int, optional): Defaults to the primary business_id.

        Returns:
            List of eversign.Document object for success, raises Exception for failure.

        """
        if type in ['templates', 'templates_archived', 'template_drafts']:
            return self._request('/document', business_id=business_id, params={'type': type},
                                 return_type=Document)
        else:
            return Exception

    def list_documents(self, type="all", business_id=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#list-documents

        Lists all the templates with specified type.

        Args:
            type (str): Allowed values:
                - "all"
                - "my_action_required"
                - "waiting_for_others"
                - "completed"
                - "drafts"
                - "cancelled"
                Defaults to "all"
            business_id (int, optional): Defaults to the primary business_id.

        Returns:
            List of eversign.Document object for success, raises Exception for failure.

        """
        if type in ['all', 'my_action_required', 'waiting_for_others', 'completed', 'drafts', 'cancelled']:
            return self._request('/document', business_id=business_id, params={'type': type},
                                 return_type=Document)

    def send_reminder(self, document, signer_id, document_hash=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#send-reminder

        Sends a reminder email to the specified document and signer.

        Args:
            document (eversign.Document)
            signer_id (int)
            document_hash (str, optional): If a document_hash is specified, it will override the document argument.

        Returns:
            JSON Response from the API

        """
        return self._request('/send_reminder', method="POST", data={
            'document_hash': document_hash or document.document_hash,
            'signer_id': signer_id
            }
        )

    def cancel_document(self, document, business_id=None, document_hash=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#cancel-document

        Cancels a document.

        Args:
            document (eversign.Document)
            business_id (int, optional): Defaults to the primary business_id.
            document_hash (str, optional): If a document_hash is specified, it will override the document argument.

        Returns:
            True for success, raises exception on failure.

        """
        return self.delete_document(document, business_id=business_id, cancel=1, document_hash=document_hash)

    def delete_document(self, document, business_id=None, cancel=None, document_hash=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#delete-document

        Deletes a document, only drafts and cancelled documents can be deleted.

        Args:
            document (eversign.Document)
            business_id (int, optional): Defaults to the primary business_id.
            cancel (bool, optional)
            document_hash (str, optional): If a document_hash is specified, it will override the document argument.

        Returns:
            True for success, raises exception on failure.

        """
        params = dict()
        if type(document) is Document:
            if document.is_cancelled or document.is_draft:
                params['document_hash'] = document.document_hash
            else:
                raise Exception(
                    'Only drafts and cancelled documents can be deleted')
        elif document_hash:
            params['document_hash'] = document_hash
        else:
            raise Exception('Please provide a document or a document hash')

        if cancel:
            params['cancel'] = cancel

        return self._request('/document', "DELETE", business_id=business_id, params=params)

    def download_final_pdf(self, document, path, business_id=None, audit_trail=1, document_hash=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#download-final-pdf

        Downloads the final signed PDF to the specified path.

        Args:
            document (eversign.Document)
            path (str): Local path on the file system
            business_id (int, optional): Defaults to the primary business_id.
            audit_trail (int, optional): Defaults to 1.
            document_hash (str, optional): If a document_hash is specified, it will override the document argument.

        Returns:
            True for success, raises exception on failure.
        """
        return self._download('/download_final_document', path, params={
            'business_id': business_id or self.business_id,
            'document_hash': document_hash or self._get_document_hash(document),
            'audit_trail': audit_trail
        })

    def download_raw_document(self, document, path, business_id=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#download-original-pdf

        Deletes a document, only drafts and cancelled documents can be deleted.

        Args:
            document (eversign.Document)
            path (str): Local path on the file system
            business_id (int, optional): Defaults to the primary business_id.

        Returns:
            True for success, raises exception on failure.
        """
        return self._download('/download_raw_document', path, params={
            'business_id': business_id or self.business_id,
            'document_hash': self._get_document_hash(document)
        })

    def upload_file(self, path, business_id=None):
        """
        Documentation: https://eversign.com/api/documentation/methods#upload-file

        Uploads a file to Eversign.

        Args:
            path (str): Local path on the file system
            business_id (int, optional): Defaults to the primary business_id.

        Returns:
            JSON response from the API, exception on error
        """
        try:
            url = self.api_base + '/file'
            params = dict()
            params['access_key'] = self.access_key
            params['business_id'] = business_id or self.business_id

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

    def _request(self, url, method="GET", business_id=None, params=dict(), data=None,
                 return_type=None):
        url = self.api_base + url

        params['access_key'] = self.access_key
        params['business_id'] = business_id or self.business_id

        try:
            if method in ["GET", "DELETE"]:
                response = requests.request(method, url, params=params)

            elif method == "POST":
                if self.debug:
                    logging.debug(data)
                response = requests.request(
                    method, url, params=params, json=data)

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
