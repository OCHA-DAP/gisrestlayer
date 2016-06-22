import json
import mixpanel
import logging
import requests

import analyticsapi.exceptions.exceptions as exceptions

logger = logging.getLogger(__name__)

def send_event_task(task_arguments):
    '''
    :param task_arguments: should contain at least: event_name, ga_meta, mixpanel_meta, mixpanel_tracking_id,
     Also mixpanel_token depends on the flag send_mixpanel
    :type task_arguments: dict
    '''
    if not task_arguments:
        raise exceptions.EmptyTaskArgumentException('Task arguments seem to be empty')

    send_to_mixpanel = task_arguments.get('send_mixpanel')
    send_to_ga = task_arguments.get('send_ga')

    if send_to_mixpanel:
        MixpanelSendEvent(task_arguments).send_event()
    if send_to_ga:
        GoogleAnalyticsSendEvent(task_arguments).send_event()
    if not send_to_ga and not send_to_mixpanel:
        raise exceptions.MissingTaskArgumentException('No flag to send to either Mixpanel or GA')


class AbstractSendEvent(object):
    def __init__(self, task_arguments):
        '''
        :param task_arguments: task arguments
        :type task_arguments: dict
        '''
        # self.task_arguments = task_arguments
        if not task_arguments.get('event_name'):
            raise exceptions.MissingTaskArgumentException('Missing event name')

        self.event_name = task_arguments.get('event_name')

    def send_event(self):
        '''
        This should be implemented in the subclass
        '''
        pass


class MixpanelSendEvent(AbstractSendEvent):

    def __init__(self, task_arguments):
        super(MixpanelSendEvent, self).__init__(task_arguments)
        if not task_arguments.get('mixpanel_token'):
            raise exceptions.MissingTaskArgumentException('Missing mixpanel token')
        self.mixpanel_token = task_arguments.get('mixpanel_token')

        if not task_arguments.get('mixpanel_tracking_id'):
            raise exceptions.MissingTaskArgumentException('Missing mixpanel tracking id')
        self.mixpanel_tracking_id = task_arguments.get('mixpanel_tracking_id')

        self.event_meta = task_arguments.get('mixpanel_meta')

    def send_event(self):

        mp = mixpanel.Mixpanel(self.mixpanel_token)
        mp.track(self.mixpanel_tracking_id, self.event_name, self.event_meta)

class GoogleAnalyticsSendEvent(AbstractSendEvent):

    def __init__(self, task_arguments):
        super(GoogleAnalyticsSendEvent, self).__init__(task_arguments)

        if not task_arguments.get('ga_meta'):
            raise exceptions.MissingTaskArgumentException('Missing google analytics meta')
        self.event_meta = task_arguments.get('ga_meta')

    def send_event(self):
        response = requests.post('https://ssl.google-analytics.com/collect', data=self.event_meta, timeout=3)
        response.raise_for_status()
        logger.info(response.text)
        pass