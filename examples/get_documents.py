import sys
import config
from pprint import pprint
sys.path.append("..")
import eversign


client = eversign.Client(config.access_key)

for document in client.list_documents():
    signer = document.signers[0] if len(document.signers) > 0 else None
    name = signer.name
    field = document.fields[0] if len(document.fields) > 0 else None
    pprint(signer)
    pprint(name)
    pprint(field)
