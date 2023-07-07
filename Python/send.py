import time
import base64
import hmac
import urllib.parse
import json
import paho.mqtt.client as mqtt
from time import sleep
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, CERT_REQUIRED
import os
from dotenv import load_dotenv
load_dotenv()

IOT_HUB_NAME = "streaming-test"
IOT_HUB_DEVICE_ID = "device01"

ENDPOINT = f"{IOT_HUB_NAME}.azure-devices.net/devices/{IOT_HUB_DEVICE_ID}"
DEVICE_KEY = os.getenv("AZURE_IOT_HUB_DEVICE_KEY")
PUBLISH_TOPIC_TO_IOT_HUB = f"devices/{IOT_HUB_DEVICE_ID}/messages/events/"

def generate_sas_token(uri, key, expiry=3600):
    ttl = int(time.time()) + expiry
    urlToSign = urllib.parse.quote(uri, safe='')
    sign_key = "%s\n%d" % (urlToSign, int(ttl))
    h = hmac.new(base64.b64decode(key), msg="{0}\n{1}".format(urlToSign, ttl).encode('utf-8'), digestmod='sha256')
    signature = urllib.parse.quote(base64.b64encode(h.digest()), safe='')
    return "SharedAccessSignature sr={0}&sig={1}&se={2}".format(urlToSign,urllib.parse.quote(base64.b64encode(h.digest()),safe=''), ttl)

def on_connect(mqtt_client, obj, flags, rc):
    print("connect: " + str(rc))

def on_disconnect(client, userdata, rc):
    print("Device disconnected with result code: " + str(rc))

def on_publish(mqtt_client, obj, mid):
    print("publish: " + str(mid))

mqtt_client = mqtt.Client(client_id=IOT_HUB_DEVICE_ID, protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_publish = on_publish

mqtt_client.username_pw_set(username=IOT_HUB_NAME + ".azure-devices.net/" + IOT_HUB_DEVICE_ID + "/?api-version=2021-04-12", 
                            password=generate_sas_token(ENDPOINT, DEVICE_KEY))

ssl_context = SSLContext(protocol=PROTOCOL_TLS_CLIENT)
ssl_context.load_default_certs()
ssl_context.verify_mode = CERT_REQUIRED
ssl_context.check_hostname = True
mqtt_client.tls_set_context(context=ssl_context)

mqtt_client.connect(host=IOT_HUB_NAME + ".azure-devices.net", port=8883, keepalive=120)

# send telemetry
payload = {
    "message": "Hello World"
}

mqtt_client.publish(f"{PUBLISH_TOPIC_TO_IOT_HUB}$.ct=application%2Fjson&$.ce=utf-8", payload=json.dumps(payload), qos=1)

# start the MQTT processing loop
mqtt_client.loop_start()
# mqtt_client.loop_forever()