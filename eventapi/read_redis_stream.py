import argparse
import json
from hdx_redis_lib import connect_to_hdx_event_bus, RedisKeyValueStore, RedisConfig

parser = argparse.ArgumentParser()
parser.add_argument('--host', type=str, default='redis', help='Redis host (default: redis)')
parser.add_argument('--port', type=int, default=6379, help='Redis port (default: 6379)')
parser.add_argument('--db', type=int, default=7, help='Redis database number (default: 7)')
parser.add_argument('--clean', type=bool, default=True, help='Clean stream after reading (default: True)')
args = parser.parse_args()

# Define the stream name and the ID to start reading from
stream_name = 'hdx_event_stream'
group_name = 'default_group'
consumer_name = 'consumer-1'
last_id = 0

# Connect to Redis
# r = redis.Redis(host=args.host, port=args.port, db=args.db)
event_bus = connect_to_hdx_event_bus(
    stream_name, group_name, consumer_name,
    RedisConfig(host=args.host, port=args.port, db=args.db)
)
# kv = RedisKeyValueStore(RedisConfig(host=args.host, port=args.port, db=args.db))

# Continuously read events from the stream
while True:
    # Read events from the stream starting from the last ID
    # events = r.xread({stream_name: last_id}, block=5000)
    event = event_bus.read_hdx_event()
    if event:
        print(json.dumps(event, ensure_ascii=False, indent=4))

    # Process each event
    # for event_tuple in events:
    #     for event_id, event_data in event_tuple[1]:
    #         body_bytes = event_data.get(b'body')
    #         if body_bytes:
    #             body = json.loads(body_bytes.decode('utf-8'))
    #             # Print the event data
    #             print(json.dumps(body, ensure_ascii=False, indent=4))
    #
    #         # Update the last ID to the ID of the last event processed
    #         last_id = event_id
    #         if args.clean:
    #             # delete the event from the stream
    #             r.xdel(stream_name, event_id)