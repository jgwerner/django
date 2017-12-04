import os
import boto3
import requests
import uuid
import zipfile
from functools import partial
from django.conf import settings
from django.utils.functional import cached_property


class LambdaDeployer:
    def __init__(self, deployment):
        self.deployment = deployment
        self.lmbd = boto3.client('lambda')
        self.api_gateway = boto3.client('apigateway')

    def deploy(self):
        if 'function_arn' in self.deployment.config:
            self.lmbd.update_function_code(
                FunctionName=str(self.deployment.pk),
                ZipFile=self.prepare_package(),
            )
            return
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
        if 'rest_api_id' not in self.deployment.config:
            self.create_project_api()

        # create resource
        resource_resp = self.api_gateway.create_resource(
            restApiId=self.deployment.config['rest_api_id'],
            pathPart=str(self.deployment.pk),
            parentId=self.api_root
        )

        self.deployment.config['resource_id'] = resource_resp['id']

        # create POST method
        self.api_gateway.put_method(
            restApiId=self.deployment.config['rest_api_id'],
            resourceId=resource_resp['id'],
            httpMethod="GET",
            authorizationType="NONE",
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
            restApiId=self.deployment.config['rest_api_id'],
            resourceId=resource_resp['id'],
            httpMethod="GET",
            type="AWS_PROXY",
            integrationHttpMethod="POST",
            uri=uri,
        )
        uri_data['aws-api-id'] = self.deployment.config['rest_api_id']
        source_arn = "arn:aws:execute-api:{aws-region}:{aws-acct-id}:{aws-api-id}/*/GET/{lambda-function-name}".format(**uri_data)

        self.lmbd.add_permission(
            FunctionName=str(self.deployment.pk),
            StatementId=uuid.uuid4().hex,
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=source_arn
        )
        self.deployment.config['endpoint'] = f"https://{self.deployment.config['rest_api_id']}.execute-api.{settings.AWS_DEFAULT_REGION}.amazonaws.com/{self.deployment.name}"
        self.deployment.save()

    def delete(self):
        if 'resource_id' in self.deployment.config:
            self.lmbd.delete_function(FunctionName=str(self.deployment.pk))
            self.api_gateway.delete_resource(
                restApiId=self.deployment.config['rest_api_id'],
                resourceId=self.deployment.config['resource_id']
            )

    @cached_property
    def api_root(self):
        resp = self.api_gateway.get_resources(restApiId=self.deployment.config['rest_api_id'])
        return next(x for x in resp['items'][::-1] if x['path'] == '/')['id']

    def create_project_api(self):
        resp = self.api_gateway.create_rest_api(
            name=f'{self.deployment.project.name}-{self.deployment.project.pk}',
        )
        self.deployment.config['rest_api_id'] = resp['id']

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
