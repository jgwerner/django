import os
import re
import boto3
import urllib.request
import uuid
import tempfile
import zipfile
from functools import partial
from botocore.exceptions import ClientError
from django.conf import settings
from django.utils.functional import cached_property


class LambdaDeployer:
    def __init__(self, deployment, lambda_client=None, api_gateway_client=None, statement_id=None):
        self.deployment = deployment
        self.lmbd = lambda_client or boto3.client('lambda')
        self.api_gateway = api_gateway_client or boto3.client('apigateway')
        self.stage = "prod"
        self.lambda_version = self.lmbd.meta.service_model.api_version
        self.api_name = ''
        self.statement_id = statement_id or uuid.uuid4().hex
        self.function_method = self.deployment.config.get('method', 'GET')

    def deploy(self):
        if not self.api_id:
            # hack to set cached property
            self.__dict__['api_id'] = self._create_api()
        try:
            self._deploy()
        except Exception as e:
            self.deployment.save()
            raise

    def _deploy(self):
        self.deployment.config['rest_api_id'] = self.api_id
        if 'endpoint' in self.deployment.config:
            self.lmbd.update_function_code(
                FunctionName=str(self.deployment.pk),
                ZipFile=self.prepare_package(),
            )
            return
        if 'function_arn' not in self.deployment.config:
            self._create_lambda_function()
        if 'resource_id' not in self.deployment.config:
            resource = self._create_api_resource()

            self._create_api_method(resource)

            self._create_api_integration(resource)

            self._add_permission()

            self._create_deployment()

        self.deployment.config['endpoint'] = ''.join([
            f"https://{self.api_id}.execute-api.{settings.AWS_DEFAULT_REGION}.amazonaws.com/",
            f"{self.stage}/{self.deployment.pk}?access_token={self.deployment.access_token}"
        ])
        self.deployment.save()

    def delete(self):
        if 'resource_id' in self.deployment.config:
            self.lmbd.delete_function(FunctionName=str(self.deployment.pk))
            self.api_gateway.delete_resource(
                restApiId=self.api_id,
                resourceId=self.deployment.config['resource_id']
            )

    def prepare_package(self) -> bytes:
        _, tmp = tempfile.mkstemp()
        if self.deployment.framework.url:
            tmp, headers = urllib.request.urlretrieve(self.deployment.framework.url, filename=tmp)
        with zipfile.ZipFile(tmp, 'a') as package:
            join = partial(os.path.join, self.deployment.volume_path)
            for user_file in self.deployment.config['files']:
                package.write(join(user_file), arcname=user_file)
        out = b''
        with open(tmp, 'rb') as tp:
            out = tp.read()
        os.remove(tmp)
        return out

    @cached_property
    def api_root(self):
        resp = self.api_gateway.get_resources(restApiId=self.api_id)
        # reversing items because root is usually at the end
        items = resp['items'][::-1]
        for resource in items:
            if resource['path'] == '/':
                return resource['id']

    @cached_property
    def api_id(self) -> str:
        """
        API naming pattern: deploymentApi-{number}
        """
        resp = self.api_gateway.get_rest_apis(limit=60)
        current = self._get_current_object(resp)
        self.api_name = current['name']
        return current['id']

    @cached_property
    def authorizer_id(self) -> str:
        """
        Authorizer naming pattern: deploymentAuthorizer-{api_number}
        """
        resp = self.api_gateway.get_authorizers(restApiId=self.api_id)
        return self._get_current_object(resp)['id']

    def _get_current_object(self, resp: dict) -> dict:
        regex = re.compile(r'deployment[A-Z][a-z]+-\d+')
        deployment_objs = filter(lambda x: regex.match(x['name']), resp['items'])
        try:
            current = max(deployment_objs, key=lambda x: int(x['name'].split('-')[1]))
        except ValueError:
            return {'id': '', 'name': ''}
        return current

    def _create_api(self):
        api_number = int(self.api_name.split('-')[1]) if self.api_name else -1
        api_resp = self.api_gateway.create_rest_api(name=f'deploymentApi-{api_number+1}')

        self.api_gateway.create_authorizer(
            restApiId=api_resp['id'],
            name=f'deploymentAuthorizer-{api_number+1}',
            type='REQUEST',
            identitySource='method.request.querystring.access_token',
            authorizerUri=''.join([
                f'arn:aws:apigateway:{settings.AWS_DEFAULT_REGION}:',
                f'lambda:path/{self.lambda_version}/functions/',
                f'{settings.AWS_LAMBDA_AUTHORIZER}/invocations'
            ]),
            authorizerCredentials=settings.AWS_AUTHORIZER_ROLE,
        )
        return api_resp['id']

    def _create_lambda_function(self):
        resp = self.lmbd.create_function(
            FunctionName=str(self.deployment.pk),
            Runtime=self.deployment.runtime.name,
            Code={
                'ZipFile': self.prepare_package()
            },
            MemorySize=1536,
            Handler=self.deployment.config['handler'],
            Timeout=300,
            Role=settings.AWS_DEPLOYMENT_ROLE,
        )
        self.deployment.config['function_arn'] = resp['FunctionArn']

    def _create_api_resource(self):
        try:
            resource_resp = self.api_gateway.create_resource(
                restApiId=self.api_id,
                pathPart=str(self.deployment.pk),
                parentId=self.api_root
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'LimitExceededException':
                self.__dict__['api_id'] = self._create_api()
                return self._create_api_resource()
            else:
                raise

        self.deployment.config['resource_id'] = resource_resp['id']
        return resource_resp

    def _create_api_method(self, resource):
        self.api_gateway.put_method(
            restApiId=self.api_id,
            resourceId=resource['id'],
            httpMethod=self.function_method,
            authorizationType="CUSTOM",
            authorizerId=self.authorizer_id,
            apiKeyRequired=False,
        )

    def _create_api_integration(self, resource):
        uri = ''.join([
            f"arn:aws:apigateway:{settings.AWS_DEFAULT_REGION}:",
            f"lambda:path/{self.lambda_version}/functions/",
            f"{self.deployment.config['function_arn']}/invocations"
        ])

        # create integration
        self.api_gateway.put_integration(
            restApiId=self.api_id,
            resourceId=resource['id'],
            httpMethod=self.function_method,
            type="AWS_PROXY",
            integrationHttpMethod="POST",
            uri=uri,
        )

    def _add_permission(self):
        source_arn = ''.join([
            f"arn:aws:execute-api:{settings.AWS_DEFAULT_REGION}:",
            f"{settings.AWS_ACCOUNT_ID}:{self.api_id}/*/{self.function_method}/{self.deployment.pk}"
        ])
        self.lmbd.add_permission(
            FunctionName=str(self.deployment.pk),
            StatementId=self.statement_id,
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=source_arn
        )

    def _create_deployment(self):
        self.api_gateway.create_deployment(
            restApiId=self.api_id,
            stageName=self.stage,
        )
