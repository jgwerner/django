import os

import requests
import boto3
import logging
import json
from requests.auth import AuthBase

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class ECSEvents:
    def __init__(self):
        self.url_kwargs = dict(
            namespace='',
            project_id='',
            server_id='',
            token=''
        )
        self.api = None

    def __call__(self, event, context):
        logger.info(f"Handling event: {event}")
        logger.info(f"Event context: {context}")
        for record in event['Records']:
            sns = record['Sns']
            if sns['Type'] == 'Notification':
                message = json.loads(sns['Message'])
                self.set_url_kwargs(message['detail']['taskDefinitionArn'])
                self.api = APIClient(self.url_kwargs)
                funcs = {
                    'STOPPED': [self.create_server_delete_action, self.server_end_stats],
                    'RUNNING': [self.server_add_stats],
                }[message['detail']['desiredStatus']]
                for func in funcs:
                    func(message)

    def create_server_delete_action(self, event):
        logger.info(f"Creates server remove action for server: {self.url_kwargs['server_id']}")
        action = dict(
            action_name='stop',
            action="Server stop",
            is_user_action=False,
            method='POST',
            object_id=self.url_kwargs['server_id'],
            content_type='server',
            state=4,  # actions.models.Action.SUCCESS
            user_agent="ECS stats",
            start_date=event['detail']['createdAt']
        )
        resp = self.api.create_action(action)
        resp.raise_for_status()

    def server_add_stats(self, event):
        logger.info(f"Creates server stats: {self.url_kwargs['server_id']}")
        stats = dict(
            size=0,
            start=event['detail']['createdAt']
        )
        resp = self.api.add_server_stats(stats)
        resp.raise_for_status()

    def server_end_stats(self, event):
        logger.info(f"Updates server stats: {self.url_kwargs['server_id']}")
        stats = dict(stop=event['detail']['createdAt'])
        resp = self.api.update_server_stats(stats)
        resp.raise_for_status()

    def set_url_kwargs(self, task_definition_arn):
        ecs = boto3.client('ecs')
        task_def = ecs.describe_task_definition(taskDefinition=task_definition_arn)
        cmd = task_def['taskDefinition']['containerDefinitions'][0]['command']
        for arg in cmd:
            if '-ns=' in arg:
                self.url_kwargs['namespace'] = arg.split('=')[1]
            if '-projectID=' in arg:
                self.url_kwargs['project_id'] = arg.split('=')[1]
            if '-serverID=' in arg:
                self.url_kwargs['server_id'] = arg.split('=')[1]
            if '-key=' in arg:
                self.url_kwargs['token'] = arg.split('=')[1]


class APIAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = f'JWT {self.token}'
        return r


class APIClient(requests.Session):
    def __init__(self, url_kwargs):
        super().__init__()
        self.auth = APIAuth(url_kwargs['token'])
        self.url_kwargs = url_kwargs

    def request(self, method, url, **kwargs):
        api_url = ''.join([
            f'{os.environ.get("APP_SCHEME")}',
            f'/{os.environ.get("TBS_DEFAULT_VERSION")}',
            url
        ])
        return super().request(method, api_url, **kwargs)

    def create_action(self, action):
        url = '/actions/create/'
        return self.post(url, action)

    def add_server_stats(self, stats):
        url = ''.join([
            f'/{self.url_kwargs["namespace"]}',
            f'/projects/{self.url_kwargs["project_id"]}',
            f'/servers/{self.url_kwargs["server_id"]}',
            '/run-stats/'
        ])
        return self.post(url, stats)

    def update_server_stats(self, stats):
        url = ''.join([
            f'/{self.url_kwargs["namespace"]}',
            f'/projects/{self.url_kwargs["project_id"]}',
            f'/servers/{self.url_kwargs["server_id"]}',
            '/run-stats/update_latest/'
        ])
        return self.post(url, stats)


handle = ECSEvents()
