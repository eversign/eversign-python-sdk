# eversign Python SDK #

eversign Python SDK is the official Python Wrapper around the eversign [API](https://eversign.com/api/documentation).

**Quick Links:**
  - [Create Document Example](/examples/create_document.py)
  - [Download Document Example](/examples/download_document.py)
  - [Get Documents Example](/examples/get_documents.py)

## Installation

Install from npm:
````sh
pip install eversign
````

Install from code:
````sh
pip install git+https://github.com/eversign/eversign-python-sdk.git
````

## Usage

All eversign API requests are made using the `Client` class, which contains all methods for creating, retrieving and saving documents. This class must be initialized with your API access key string. [Where is my API access key?](https://eversign.com/api/documentation/intro#api-access-key)

Please also specify the ID of the eversign business you would like this API request to affect. [Where is my Business ID?](https://eversign.com/api/documentation/intro#business-selection)

In your Python application, import `eversign` and pass authentication information to initialize it:

````python
import eversign
client = eversign.Client("ACCESS_KEY")
````

The client will automatically pick up the primary business to use.

### Fetch businesses
Using the `get_businesses()` function all businesses on the eversign account will be fetched and listed along with their Business IDs.

````python
print(client.get_businesses()[0])
````

### Create document from template [Method: Use Template]
To create a document based on an already created template you can use the class `Template` (they are identical). In order to identify which template should be used, please set the template's ID `template_id = "MY_TEMPLATE_ID"`.

````python
template = eversign.Template()
template.template_id = "MY_TEMPLATE_ID"
template.title = "Tile goes here"
template.message = "test message"
````

#### Fill signing roles [Method: Use Template]
A template's signing and CC roles are filled just using the functions below. Each role is identified using the `role` field, must carry a name and email address and is appended to the document using the `add_signer()` function.

````python
signer = eversign.Signer()
signer.role = "Testrole"
signer.name = "John Doe"
signer.email = "john.doe@eversign.com"

template.add_signer(signer)
````

#### Saving the document object [Method: Use Template]
Your document object can now be saved using the `create_document_from_template()` function. Once this function has been called successfully, your document is created and the signing process is started.

````python
document = client.create_document_from_template(template)
````

### Creating a document [Method: Create Document]
A document is created by instantiating the `Document` object and setting your preferred document properties. All available methods can be found inside our extensive [Create Document Example](/examples/create_document.js).

````python
document = eversign.Document()
document.template_id = "MY_TEMPLATE_ID"
document.title = "Tile goes here"
document.message = "test message"
````

#### Adding signers to a document [Method: Create Document]
Signers are added to an existing document object by instantiating the `Signer` object and appending each signer to the document object. Each signer object needs to come with a Signer ID, which is later used to assign fields to the respective signer. If no Signer ID is specified, the `add_signer()` method will set a default incremented Signer ID. Each signer object also must contain a name and email address and is appended to the document using the `add_signer()` method.

````python
signer = eversign.Signer()
signer.role = "Testrole"
signer.name = "John Doe"
signer.email = "john.doe@eversign.com"

document.add_signer(signer)
````

#### Adding recipients (CCs) to a document [Method: Create Document]
Recipients (CCs) are added by instantiating the `Recipient` object and appending each recipient to the document object. Just like signers, recipients must carry a name and email address.

````python
recipient = eversign.Recipient()
recipient.role = "Testrole"
recipient.name = "John Doe"
recipient.email = "john.doe@eversign.com"

document.add_recipient(recipient)
````

#### Adding files to the Document [Method: Create Document]
Files are added to a document by instantiating an `File` object. The standard way of choosing a file to upload is appending the file's path using the `file_url` field and then appending your file using the `add_file()` method.

````python
file = eversign.File()
file.file_name = "Test"
file.file_url = "test.pdf"

document.add_file(file)
````

#### Adding fields [Method: Create Document]
There is a number of fields that can be added to a document, each coming with different options and parameters. ([Full list of fields »](https://eversign.com/api/documentation/fields))

A field is appended to the document using the `add_field(field)` method.

Signature and Initials fields are required to be assigned to a specific signer. Fields are assigned to a signer by setting the **Signer ID** `signer` field.

````python
field = eversign.SignatureField()

field.identifier = "Test Signature"
field.x = "120.43811219947"
field.y = "479.02760463045"
field.page = 1
field.signer = 5
field.width = 120
field.height = 35
field.required = 1

document.add_field(field)
````

#### Saving a document [Method: Create Document]
A document is saved and sent out by passing the final document object into the `create_document` method. The API will return the entire document object array in response.

```python
saved_document = client.create_document(document)
```

#### Loading a document

A document is loaded by either passing a `Document` into the `get_document()` function, or passing its document hash `get_document(document_hash="MY_HASH")`. Attention: a provided document_hash overrides a passed document.

```python
document = client.get_document(document_hash="MY_HASH")
```

#### Downloading the raw or final document
A document can be downloaded either in its raw or in its final (completed) state. In both cases, the respective method must contain the document object and a path to save the PDF document to. When downloading a final document, you can choose to attach the document's Audit Trail by setting the third parameter to `1`.

```python
client.download_final_pdf(document, "final.pdf")
# audit_trail defaults to 1 (True)
# client.download_final_pdf(document, "final.pdf", audit_trail=0)
client.download_raw_document(document, "raw.pdf")
```

#### Get a list of documents or templates
The Client class is also capable fo listing all available documents templates based on their status. Each method below returns an array of document objects.

```python
client.list_documents()
client.list_templates()

# Other Methods for getting documents are:

client.list_documents("my_action_required")
client.list_documents("waiting_for_others")
client.list_documents("completed")
client.list_documents("drafts")
client.list_documents("cancelled")

client.list_templates("templates_archived")
client.list_templates("template_drafts")

```

#### Delete or cancel a document
A document is cancelled or deleted using the methods below.

```python
client.delete_document(document);
client.cancel_document(document);
```


### Contact us
Any feedback? Please feel free to [contact our support team](https://eversign.com/contact).