from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from configparser import ConfigParser
import requests
import time

config = ConfigParser()
config.read("config.ini")

client_id = config["DEFAULT"]["client_id"]
client_secret = config["DEFAULT"]["client_secret"]
token_url = config["DEFAULT"]["access_token_url"]

http_url = config["DEFAULT"]["http_url"]

certificate = config["DEFAULT"]["certificate"]
certificate_key = config["DEFAULT"]["certificate_key"]
certificate_chain = config["DEFAULT"]["certificate_chain"]

session = requests.Session()
session.cert = (certificate, certificate_key)
session.verify = certificate_chain
session.headers.update({"content-type": "application/json"})

client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(
    token_url=token_url,
    client_id=client_id,
    client_secret=client_secret,
)

order = """
[
  {
    "@class": "MarketplaceOrderDTO",
    "accountSegment": {
      "entityId": 111111,
      "entityType": "ACCOUNTSEGMENT"
    },
    "asset": {
      "entityType": "STOCK",
      "symbolType": "ISIN",
      "symbolIdentifier": "US0079031078"
    },
    "counterpart": {
      "entityType": "COUNTERPART",
      "symbolType": "BIC",
      "symbolIdentifier": "JBBRFRPP"
    },
    "evaluationCurrency": {
      "entityType": "CURRENCY",
      "iso4217Code": "EUR"
    },
    "expiration": {
      "@class": "ExpirationDTO",
      "type": "GOOD_TILL_CANCEL"
    },
    "limit": {
      "@class": "LimitDTO",
      "type": "MARKET"
    },
    "marketplace": {
      "entityType": "MARKETPLACE",
      "symbolType": "MIC",
      "symbolIdentifier": "XGRM"
    },
    "orderAction": "BUY_OPEN",
    "volume": {
      "quantity": 1000,
      "unit": {
        "@class": "PIECE"
      }
    }
  }
]
"""

order_response = session.post(
    f"{http_url}/ordermanagement/orders/queue",
    order,
    headers={"Authorization": f"Bearer {token['access_token']}"},
)

if order_response.status_code != 200:
    print(f"Unable to create order: {order_response.status_code}: {order_response.text}")
    exit(1)

order_id = order_response.json()[0]["versionedEntityId"]["entityId"]
print(f"Successfully created order with id {order_id}")

cre_run_parameters = """
{
  "accountSegmentId": 111111,
  "scope": "PRE_TRADE",
  "priceSource": "CLOSING",
  "runMode": "RUN"
}
"""

cre_run_response = session.post(
    f"{http_url}/compliance/perform",
    cre_run_parameters,
    headers={"Authorization": f"Bearer {token['access_token']}"},
)

if cre_run_response.status_code != 200:
    print(
        f"Unable to start cre run: {cre_run_response.status_code}: {cre_run_response.text}"
    )
    exit(1)

cre_run_id = cre_run_response.json()["versionedEntityId"]["entityId"]
print(f"Successfully startet cre run with id {cre_run_id}")

time.sleep(1)  # wait for CRE run to finish instead

active_order_reponse = session.post(
    f"{http_url}/ordermanagement/orders/activate/{cre_run_id}",
    headers={"Authorization": f"Bearer {token['access_token']}"},
)

if active_order_reponse.status_code != 200:
    print(
        f"Unable to activate order: {active_order_reponse.status_code}: {active_order_reponse.text}"
    )
    exit(1)

release_order_response = session.post(
    f"{http_url}/ordermanagement/orders/{order_id}/release",
    headers={"Authorization": f"Bearer {token['access_token']}"},
)

if release_order_response.status_code != 200:
    print(
        f"Unable to release order: {release_order_response.status_code}: {release_order_response.text}"
    )
    exit(1)
