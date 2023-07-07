require('dotenv').config()
const mqtt = require('mqtt')
const crypto = require('crypto');

const host = `${process.env.EVENT_HUB_NAME}.azure-devices.net`
const port = '8883'
const connectUrl = `mqtts://${host}:${port}`
const endpoint = `${host}/devices/${process.env.IOT_HUB_DEVICE_ID}`

const generateSasToken = function(resourceUri, signingKey, expiresInMins=60) {
    resourceUri = encodeURIComponent(resourceUri);

    // Set expiration in seconds
    var expires = (Date.now() / 1000) + expiresInMins * 60;
    expires = Math.ceil(expires);
    var toSign = resourceUri + '\n' + expires;

    // Use crypto
    var hmac = crypto.createHmac('sha256', Buffer.from(signingKey, 'base64'));
    hmac.update(toSign);
    var base64UriEncoded = encodeURIComponent(hmac.digest('base64'));

    // Construct authorization string
    var token = "SharedAccessSignature sr=" + resourceUri + "&sig="
    + base64UriEncoded + "&se=" + expires;
    return token;
};

const client = mqtt.connect(connectUrl, {
  clientId: process.env.IOT_HUB_DEVICE_ID,
  clean: false,
  connectTimeout: 4000,
  username: `${process.env.EVENT_HUB_NAME}.azure-devices.net/${process.env.IOT_HUB_DEVICE_ID}/?api-version=2021-04-12`,
  password: generateSasToken(endpoint, process.env.DEVICE_KEY),
  reconnectPeriod: 1000,
})

const topic = `devices/${process.env.IOT_HUB_DEVICE_ID}/messages/events/$.ct=application%2Fjson&$.ce=utf-8`

const formatter = new Intl.DateTimeFormat('zh-TW', {
    year: 'numeric',
    month: 'numeric',
    day: 'numeric',
    hour: 'numeric',
    hour12: false,
    minute: 'numeric',
    second: 'numeric',
    timeZone: 'Asia/Taipei',
});

function wait(ms) {
    return new Promise(resolve => setTimeout(() => resolve(), ms));
};

client.on('connect', async() => {
    while(true) {
        const now = new Date();
        const datas = {
            temperature: Math.random(),
            humidity: Math.random(),
            timestamp: `${formatter.format(now)}.${now.getMilliseconds()}`,
        }
        client.publish(topic, JSON.stringify(datas), { qos: 0, retain: false }, (error) => {
            if (error) {
                console.error(error)
            }
        })
        await wait(1000);
    }
    
})