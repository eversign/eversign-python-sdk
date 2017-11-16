import sys
import config
import eversign

client = eversign.Client(config.access_key)

document_template = eversign.Template()
document_template.template_id = config.template_id
document_template.title = 'Tile goes here'
document_template.message = 'my message'

signer = eversign.Signer(name='Jane Doe', email=config.signer_email, role='Client')
document_template.add_signer(signer)

field = eversign.Field()
field.identifier = config.field_identifier
field.value = 'value 1'
document_template.add_field(field)

finished_document = client.create_document_from_template(document_template)
print(finished_document.document_hash)
