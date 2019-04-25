import os
import uuid
import oauthlib.oauth1
from requests.auth import AuthBase
from locust import HttpLocust, TaskSet
from faker import Faker

fake = Faker()

API_URL = os.getenv('API_URL')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')


def sign_request(url, body):
    client = oauthlib.oauth1.Client(
        CLIENT_ID,
        client_secret=CLIENT_SECRET,
        signature_type=oauthlib.oauth1.SIGNATURE_TYPE_BODY
    )
    return client.sign(
        url,
        http_method='POST',
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        body=body
    )

def login(l):
    response = l.client.post(
        '/auth/jwt-token-auth/',
        json={'username': ADMIN_USERNAME, 'password': ADMIN_PASSWORD},
        verify=False
    )
    return response.json()['token']


def create_project(l):
    data = {'name': fake.pystr()}
    l.client.post(f'/v1/{ADMIN_USERNAME}/projects/', json=data, verify=False)

def create_server(l):
    data = {'name': fake.pystr()}
    project = l.client.post(f'/v1/{ADMIN_USERNAME}/projects/', json=data, verify=False).json()
    data = {'name': fake.pystr(), 'config': {'type': 'jupyter'}, 'image': 'illumidesk/datascience-notebook'}
    l.client.post(f'/v1/{ADMIN_USERNAME}/projects/{project["id"]}/servers/', json=data, verify=False)


def start_server(l):
    data = {'name': fake.pystr()}
    project = l.client.post(f'/v1/{ADMIN_USERNAME}/projects/', json=data, verify=False).json()
    data = {'name': fake.pystr(), 'config': {'type': 'jupyter'}, 'image': 'illumidesk/datascience-notebook'}
    server = l.client.post(f'/v1/{ADMIN_USERNAME}/projects/{project["id"]}/servers/', json=data, verify=False).json()
    l.client.post(f'/v1/{ADMIN_USERNAME}/projects/{project["id"]}/servers/{server["id"]}/start/', {}, verify=False)


def auth(l):
    endpoint = '/v1/lti/'
    data = {
        'tool_consumer_instance_guid': str(uuid.uuid4()),
        'lis_person_contact_email_primary': fake.company_email(),
        'user_id': str(uuid.uuid4()),
    }
    _, _, body = sign_request(API_URL + endpoint, data)
    l.client.post(endpoint, body, verify=False,
                  headers={'Content-Type': 'application/x-www-form-urlencoded'})


class JWTAuth(AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = f'JWT {self.token}'
        return r


class LTITask(TaskSet):
    tasks = {auth: 1, create_project: 2, create_server: 3, start_server: 3}

    def on_start(self):
       token = login(self)
       self.client.auth = JWTAuth(token)

    def on_stop(self):
        self.client.auth = None


class LTISend(HttpLocust):
    task_set = LTITask
    min_wait = 5000
    max_wait = 9000
