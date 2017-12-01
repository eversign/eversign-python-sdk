import sys
import config
from pprint import pprint
sys.path.append("..")
import eversign


client = eversign.Client()

oauth_request = {
    'client_id': config.oauth_client_id,
    'client_secret': config.oauth_client_secret,
    'code': config.code,
    'state': config.state
}

token = client.request_oauth_token(oauth_request)
client.set_oauth_access_token(token)

businesses = client.get_businesses()
print(businesses[0].business_id)
