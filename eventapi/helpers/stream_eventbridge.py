import os
import boto3
import json

client = boto3.client('events',
                      region_name=os.getenv('AWS_REGION_NAME'),
                      aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                      aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                      )


def stream_events_to_eventbridge(event_list: [dict]):
    entries = [
        {
            'Source': 'hdx-event-generator',
            'DetailType': 'dataset-change-events',
            'Detail': json.dumps(event),
            'EventBusName': 'my-ckan-event-bus',
        }
        for event in event_list
    ]
    response = client.put_events(Entries=entries)
    return response
