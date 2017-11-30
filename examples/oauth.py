import sys
import config
from pprint import pprint
sys.path.append("..")
import eversign


client = eversign.Client()

options = {
    'client_id': config.oauth_client_id,
    'state': 'example'
}

url = client.generate_oauth_authorization_url(options)

print('Please authorize: ' + url)
