import os
import logging

from hdx_redis_lib import connect_to_hdx_write_only_event_bus, RedisConfig

# Connection to Redis
# redis_conn = None
event_bus = None
log = logging.getLogger(__name__)


def stream_events_to_redis(event_list: [dict]):
    global event_bus
    if event_bus is None:
        redis_stream_host = os.getenv('REDIS_STREAM_HOST', 'redis')
        redis_stream_port = os.getenv('REDIS_STREAM_PORT', 6379)
        redis_stream_db = os.getenv('REDIS_STREAM_DB', 7)

        event_bus = connect_to_hdx_write_only_event_bus(
            'hdx_event_stream',
            RedisConfig(host=redis_stream_host, port=redis_stream_port, db=redis_stream_db)
        )
    for event in event_list:
        # Add the event to the Redis stream
        log.info('Processing event type {}'.format(event['event_type']))
        event_bus.push_hdx_event(event)
        log.info('Finished processing event type {}'.format(event['event_type']))