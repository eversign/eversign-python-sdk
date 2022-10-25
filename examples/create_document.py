import sys
import config
sys.path.append("..")
import eversign

client = eversign.Client(config.access_key)

document = eversign.Document()
document.title = "Tile goes here"
document.message = "tester@gmail.com"

recipient = eversign.Recipient(name="Test", email=config.signer_email)

file = eversign.File(name="Test")
file.file_url = 'examples/raw.pdf'

signer = eversign.Signer()
signer.id = "1"
signer.name = "Jane Doe"
signer.email = config.signer_email

document.sandbox = True

# To get embedded_claim_url in response, document has to be created as a draft
# document.is_draft = True

document.add_file(file)
document.add_signer(signer)
document.add_recipient(recipient)

field = eversign.SignatureField()

field.identifier = "Test"
field.x = "120.43811219947"
field.y = "479.02760463045"
field.page = 1
field.signer = 1
field.width = 120
field.height = 35
field.required = 1


document.add_field(field)

# Add custom requester name
document.custom_requester_name = 'Custom requester name'

# Add custom requester email
document.custom_requester_email = 'custom.requester@email.com'

finished_document = client.create_document(document)
print(finished_document.document_hash)
