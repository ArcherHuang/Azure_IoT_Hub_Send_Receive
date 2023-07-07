require('dotenv').config()

const mqtt = require('mqtt')

const host = `${process.env.EVENT_HUB_NAME}.azure-devices.net`
const port = '8883'
const connectUrl = `mqtts://${host}:${port}`

const sas = "SharedAccessSignature sr=iot-hub-svc.azure-devices.net%2Fdevices%2Fdevice01&sig=QGd8dR3ec%2Ba9Mi%2F4uwx8OIip5oZ7ncO%2BUkuiJ0DOq8U%3D&se=1688714423"

const client = mqtt.connect(connectUrl, {
  clientId: process.env.IOT_HUB_DEVICE_ID,
  clean: false,
  connectTimeout: 4000,
  username: `${process.env.EVENT_HUB_NAME}.azure-devices.net/${process.env.IOT_HUB_DEVICE_ID}/?api-version=2021-04-12`,
  password: sas,
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