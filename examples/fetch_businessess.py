import sys
import config
from pprint import pprint
sys.path.append("..")
import eversign


client = eversign.Client(config.access_key)

businesses = client.get_businesses()
print(businesses[0].business_id)
