import sys
sys.path.append("..")
import eversign

client = eversign.Client("MY_KEY")

for document in client.list_documents():
    client.download_raw_document(document, 'raw.pdf')
    client.download_final_pdf(document, 'final.pdf')
    break