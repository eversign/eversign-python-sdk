import sys
sys.path.append("..")
import eversign
import pprint

client = eversign.Client("MY_KEY")

for document in client.list_documents():
    signer = document.signers[0] if len(document.signers) > 0 else None
    name = signer.name
    field = document.fields[0] if len(document.fields) > 0 else None
    pprint.pprint(signer)
    pprint.pprint(name)
    pprint.pprint(field)