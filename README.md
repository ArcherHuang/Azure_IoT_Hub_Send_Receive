# Azure_IoT_Hub_Send_Receive

## 取得 SAS Token
```
az iot hub generate-sas-token \
    --hub-name HUB-NAME \
    --device-id DEVICE-ID \
    --key-type primary \
    --duration 3600 \
    --output tsv
```