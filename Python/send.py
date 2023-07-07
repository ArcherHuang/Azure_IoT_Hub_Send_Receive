import random
import time
import base64
import hmac
import urllib.parse
import json
import paho.mqtt.client as mqtt
from time import sleep
from datetime import datetime
from ssl import SSLContext, PROTOCOL_TLS_CLIENT, CERT_REQUIRED
import os
from dotenv import load_dotenv
load_dotenv()

IOT_HUB_NAME = os.getenv("IOT_HUB_NAME")
IOT_HUB_DEVICE_ID = os.getenv("IOT_HUB_DEVICE_ID")
DEVICE_KEY = os.getenv("DEVICE_KEY")

ENDPOINT = f"{IOT_HUB_NAME}.azure-devices.net/devices/{IOT_HUB_DEVICE_ID}"
PUBLISH_TOPIC_TO_IOT_HUB = f"devices/{IOT_HUB_DEVICE_ID}/messages/events/"

def generate_sas_token(uri, key, expiry=3600):
    ttl = int(time.time()) + expiry
    urlToSign = urllib.parse.quote(uri, safe='')
    h = hmac.new(base64.b64decode(key), msg="{0}\n{1}".format(urlToSign, ttl).encode('utf-8'), digestmod='sha256')
    return "SharedAccessSignature sr={0}&sig={1}&se={2}".format(urlToSign,urllib.parse.quote(base64.b64encode(h.digest()),safe=''), ttl)

def on_connect(mqtt_client, obj, flags, rc):
    print(f"connect: {rc}")

def on_disconnect(client, userdata, rc):
    print(f"Device disconnected with result code: {rc}")

def on_publish(mqtt_client, obj, mid):
    print(f"publish: {mid}")

mqtt_client = mqtt.Client(client_id=IOT_HUB_DEVICE_ID, protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_disconnect = on_disconnect
mqtt_client.on_publish = on_publish

get_sas = generate_sas_token(ENDPOINT, DEVICE_KEY)

mqtt_client.username_pw_set(username=IOT_HUB_NAME + ".azure-devices.net/" + IOT_HUB_DEVICE_ID + "/?api-version=2021-04-12", 
                            password=get_sas)

ssl_context = SSLContext(protocol=PROTOCOL_TLS_CLIENT)
ssl_context.load_default_certs()
ssl_context.verify_mode = CERT_REQUIRED
ssl_context.check_hostname = True
mqtt_client.tls_set_context(context=ssl_context)

mqtt_client.connect(host=IOT_HUB_NAME + ".azure-devices.net", port=8883, keepalive=120)

# start the MQTT processing loop
mqtt_client.loop_start()

while True:
    # send telemetry
    payload = {
        "temperature": random.random(),
        "humidity": random.random(),
        "timestamp": datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f")
    }

    mqtt_client.publish(f"{PUBLISH_TOPIC_TO_IOT_HUB}$.ct=application%2Fjson&$.ce=utf-8", payload=json.dumps(payload), qos=1)
    mqtt_client.loop(2,10)
    time.sleep(1)

