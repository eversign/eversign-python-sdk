import sys
import config
from pprint import pprint
sys.path.append("..")
import eversign


client = eversign.Client(config.access_key)
#
# documents = client.get_all_documents()
# print(str(len(documents)) + ' all_documents found')
#
# documents = client.get_cancelled_documents()
# print(str(len(documents)) + ' cancelled_documents found')
#
# documents = client.get_action_required_documents()
# print(str(len(documents)) + ' action_required_documents found')
#
# documents = client.get_waiting_for_others_documents()
# print(str(len(documents)) + ' waiting_for_others_documents found')
#
# documents = client.get_templates()
# print(str(len(documents)) + ' templates found')
#
# documents = client.get_archived_templates()
# print(str(len(documents)) + ' archived_templates found')
#
# documents = client.get_draft_templates()
# print(str(len(documents)) + ' draft_templates found')
#

document = client.get_document_by_hash(config.document_hash)
print(document.document_hash)
# client.download_final_document_to_path(document, './final.pdf', True)
# client.download_raw_document_to_path(document, './raw.pdf')

for signer in document.signers:
    try:
        client.send_reminder_for_document(document, signer)
    except Exception as e:
        print('could not send reminder for ' + signer.email + ': ' + str(e))

try:
    client.cancel_document(document)
except Exception as e:
    print('could not cancel document: ' + str(e))

try:
    client.delete_document(document)
except Exception as e:
    print('could not delete document: ' + str(e))
