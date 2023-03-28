import os
import json
import redis

# Connection to Redis
redis_conn = None


def stream_events_to_redis(event_list: [dict]):
    global redis_conn
    if redis_conn is None:
        redis_stream_host = os.getenv('REDIS_STREAM_HOST', 'gisredis')
        redis_stream_port = os.getenv('REDIS_STREAM_PORT', 6379)
        redis_stream_db = os.getenv('REDIS_STREAM_DB', 7)

        redis_conn = redis.Redis(host=redis_stream_host, port=redis_stream_port, db=redis_stream_db)
    for event in event_list:
        # Add the event to the Redis stream
        processed_event = {
            'event_type': event['event_type'],
            'body': bytes(json.dumps(event), 'utf-8')
        }
        redis_conn.xadd('hdx_event_stream', processed_event)