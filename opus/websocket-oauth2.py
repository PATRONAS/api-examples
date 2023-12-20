from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
from websocket import WebSocketApp
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

client_id = config["DEFAULT"]["client_id"]
client_secret = config["DEFAULT"]["client_secret"]
token_url = config["DEFAULT"]["access_token_url"]

websocket_url = config["DEFAULT"]["websocket_url"]

certificate = config["DEFAULT"]["certificate"]
certificate_key = config["DEFAULT"]["certificate_key"]
certificate_chain = config["DEFAULT"]["certificate_chain"]

client = BackendApplicationClient(client_id=client_id)
oauth = OAuth2Session(client=client)
token = oauth.fetch_token(
    token_url=token_url,
    client_id=client_id,
    client_secret=client_secret,
)

def on_message(ws, message):
    print("Websocket message received")
    print(message)


def on_error(ws, error):
    print("Websocket error")
    print(error)


def on_close(ws, close_status_code, close_msg):
    print("Websocket connection closed")


def on_open(ws):
    print("Websocket connected")

ws = WebSocketApp(
    url=websocket_url,
    on_open=on_open,
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    header=[f"Authorization: Bearer {token['access_token']}"],
)

ws.run_forever(
    sslopt={
        "keyfile": certificate_key,
        "certfile": certificate,
        "ca_certs": certificate_chain
    }
)
