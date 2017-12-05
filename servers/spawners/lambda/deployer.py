import os
import re
import boto3
import requests
import uuid
import zipfile
from functools import partial
from botocore.exceptions import ClientError
from django.conf import settings
from django.utils.functional import cached_property


class LambdaDeployer:
    def __init__(self, deployment):
        self.deployment = deployment
        self.lmbd = boto3.client('lambda')
        self.api_gateway = boto3.client('apigateway')
        self.stage = "prod"

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

        if 'resource_id' not in self.deployment.config:
            # create resource
            try:
                resource_resp = self.api_gateway.create_resource(
                    restApiId=self.api_id,
                    pathPart=str(self.deployment.pk),
                    parentId=self.api_root
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'LimitExceededException':
                    self._create_api()
                else:
                    raise

            self.deployment.config['resource_id'] = resource_resp['id']

            # create POST method
            self.api_gateway.put_method(
                restApiId=self.api_id,
                resourceId=resource_resp['id'],
                httpMethod="GET",
                authorizationType="CUSTOM",
                authorizerId=self.authorizer_id,
                apiKeyRequired=False,
            )

            lambda_version = self.lmbd.meta.service_model.api_version

            uri_data = {
                "aws-region": settings.AWS_DEFAULT_REGION,
                "api-version": lambda_version,
                "aws-acct-id": settings.AWS_ACCOUNT_ID,
                "lambda-function-name": str(self.deployment.pk),
            }

            uri = "arn:aws:apigateway:{aws-region}:lambda:path/{api-version}/functions/arn:aws:lambda:{aws-region}:{aws-acct-id}:function:{lambda-function-name}/invocations".format(**uri_data)

            # create integration
            self.api_gateway.put_integration(
                restApiId=self.api_id,
                resourceId=resource_resp['id'],
                httpMethod="GET",
                type="AWS_PROXY",
                integrationHttpMethod="POST",
                uri=uri,
            )
            uri_data['aws-api-id'] = self.api_id
            source_arn = "arn:aws:execute-api:{aws-region}:{aws-acct-id}:{aws-api-id}/*/GET/{lambda-function-name}".format(**uri_data)
            self.lmbd.add_permission(
                FunctionName=str(self.deployment.pk),
                StatementId=uuid.uuid4().hex,
                Action="lambda:InvokeFunction",
                Principal="apigateway.amazonaws.com",
                SourceArn=source_arn
            )

            self.api_gateway.create_deployment(
                restApiId=self.api_id,
                stageName=self.stage,
            )

        self.deployment.config['endpoint'] = f"https://{self.api_id}.execute-api.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{self.stage}/{self.deployment.pk}?access_token={self.deployment.access_token}"
        self.deployment.save()

    def delete(self):
        if 'resource_id' in self.deployment.config:
            self.lmbd.delete_function(FunctionName=str(self.deployment.pk))
            self.api_gateway.delete_resource(
                restApiId=self.api_id,
                resourceId=self.deployment.config['resource_id']
            )

    def prepare_package(self) -> bytes:
        resp = requests.get(self.deployment.framework.url)
        resp.raise_for_status()
        tmp_path = f'/tmp/{self.deployment.pk}.zip'
        with open(tmp_path, 'wb') as tmp:
            for chunk in resp.iter_content(1024):
                if chunk:
                    tmp.write(chunk)
        with zipfile.ZipFile(tmp_path, 'a') as package:
            join = partial(os.path.join, self.deployment.volume_path)
            for user_file in self.deployment.config['files']:
                package.write(join(user_file), arcname=user_file)
        with open(tmp_path, 'rb') as tp:
            return tp.read()
        return b''

    @cached_property
    def api_root(self):
        resp = self.api_gateway.get_resources(restApiId=self.api_id)
        return next(x for x in resp['items'][::-1] if x['path'] == '/')['id']

    @cached_property
    def api_id(self) -> str:
        """
        API naming pattern: deploymentApi-{number}
        """
        resp = self.api_gateway.get_rest_apis(limit=60)
        return self._get_object_id(resp)

    @cached_property
    def authorizer_id(self) -> str:
        """
        Authorizer naming pattern: deploymentAuthorizer-{api_number}
        """
        resp = self.api_gateway.get_authorizers(restApiId=self.api_id)
        return self._get_object_id(resp)

    def _get_object_id(self, resp: dict) -> str:
        regex = re.compile(r'deployment[A-Z][a-z]+-\d+')
        deployment_objs = filter(lambda x: regex.match(x['name']), resp['items'])
        try:
            current = max(deployment_objs, key=lambda x: int(x['name'].split('-')[1]))
        except ValueError:
            return ''
        return current['id']

    def _create_api(self):
        api_number = int(self.api_id.split('-')[1]) if self.api_id else -1
        api_resp = self.api_gateway.create_rest_api(name=f'deploymentApi-{api_number+1}')

        self.api_gateway.create_authorizer(
            restApiId=api_resp['id'],
            name=f'deploymentAuthorizer-{api_number+1}',
            type='REQUEST',
            identitySource='method.request.querystring.access_token',
            authorizerUri=f'arn:aws:apigateway:{settings.AWS_DEFAULT_REGION}:lambda:path/2015-03-31/functions/{settings.AWS_LAMBDA_AUTHORIZER}/invocations',
            authorizerCredentials=settings.AWS_AUTHORIZER_ROLE,
        )
        return api_resp['id']
