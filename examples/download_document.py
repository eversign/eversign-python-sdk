import sys
sys.path.append("..")
import config
import eversign

client = eversign.Client(config.access_key)

for document in client.get_all_documents():
    client.download_raw_document_to_path(document, 'raw.pdf')
    client.download_final_document_to_path(document, 'final.pdf')
    break
