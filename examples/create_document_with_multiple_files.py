import sys
import config
sys.path.append("..")
import eversign

client = eversign.Client(config.access_key)

# Document related
document = eversign.Document()
document.title = "Tile goes here"
document.message = "tester@gmail.com"
document.sandbox = True

# Create signer
signer = eversign.Signer()
signer.id = "1"
signer.name = "Jane Doe"
signer.email = 'test@eversign.com'
document.add_signer(signer)

# Create file
file = eversign.File(name="Test")
file.file_id = 'ab4f68fc38.....84e75763927'
document.add_file(file)

# Setup fields for this file
field1 = eversign.SignatureField()
field1.identifier = "Test"
field1.x = "120.43811219947"
field1.y = "479.02760463045"
field1.page = 1
field1.signer = 1
field1.width = 120
field1.height = 35
field1.required = 1

# Assign all fields in one go
document.add_field_list([field1])

# Create one more file
file2 = eversign.File(name="Second")
file2.file_id = 'ab4f68fc386a4......e75763927'
document.add_file(file2)

# Assign all fields in one go
document.add_field_list([])

# Finish document
finished_document = client.create_document(document)
print(finished_document.document_hash)
