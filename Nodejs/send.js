require('dotenv').config()
const { Client } = require('azure-iot-device');
const  Mqtt = require('azure-iot-device-mqtt').Mqtt;
const { Message } = require('azure-iot-device');

let iotHubDeviceConnectionString = process.env.IOT_HUB_DEVICE_CONNECTION_STRING;
const client = Client.fromConnectionString(iotHubDeviceConnectionString, Mqtt);

client.open((err) => {
    if (err) {
        console.error('Error opening IoT Hub connection:', err);
    } else {
        console.log('IoT Hub connection opened');
        const message = new  Message(JSON.stringify({
            data:  'Hello from the cloud!',
        }));
        message.contentType = 'application/json';
        message.contentEncoding = 'utf-8';
        console.log('Sending message:', message.getData());
        client.sendEvent(message, (err, res) => {
            if (err) {
                console.error('Error sending message:', err);
            } else {
                console.log('Message sent to IoT device with status:', res.constructor.name);
            }
            client.close();
        });
    }
});