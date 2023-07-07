from azure.eventhub import EventHubConsumerClient
import os
from dotenv import load_dotenv
load_dotenv()

CONSUMER_GROUP = os.getenv("CONSUMER_GROUP")
EVENT_HUB_COMPATIBLE_ENDPOINT = os.getenv("EVENT_HUB_COMPATIBLE_ENDPOINT")

def on_event_batch(partition_context, events):
    for event in events:
        # print("Received event from partition: {}.".format(partition_context.partition_id))
        print(f"Received: {event.body_as_str()}")
        # print(f"Properties (set by device): {event.properties}")
        # print("System properties (set by IoT Hub): ", event.system_properties)
    partition_context.update_checkpoint()

def on_error(partition_context, error):
    if partition_context:
        print("An exception: {} occurred during receiving from Partition: {}.".format(
            error,
            partition_context.partition_id
        ))
    else:
        print("An exception: {} occurred during the load balance process.".format(error))

def main():
    client = EventHubConsumerClient.from_connection_string(
        conn_str=EVENT_HUB_COMPATIBLE_ENDPOINT,
        consumer_group=CONSUMER_GROUP,
    )
    try:
        with client:
            client.receive_batch(
                on_event_batch=on_event_batch,
                on_error=on_error
            )
    except KeyboardInterrupt:
        print("Receiving has stopped.")

if __name__ == '__main__':
    main()