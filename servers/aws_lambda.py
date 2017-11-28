import os
import boto3
import uuid
import requests
import io
import zipfile
import base64
from functools import partial
from django.conf import settings
from servers.models import Deployment


class LambdaDeployer:
    def __init__(self, deployment: Deployment):
        self.deployment = deployment
        self.lmbd = boto3.client('lambda')
        self.api_geatway = boto3.client('apigateway')

    def deploy(self):
        resp = self.lmbd.create_function(
            FunctionName=self.deployment.name,
            Runtime=self.deployment.runtime.name,
            Code={
                'ZipFile': self.prepare_package()
            },
            MemorySize=1536,
            Handler=self.deployment.config['handler'],
            Timeout=300,
            Tags={'STAGE': self.deployment.stage}
        )
        self.deployment.config['function_arn'] = resp['FunctionArn']
        if 'rest_api_id' not in self.deployment.config:
            self.create_project_api()
        self.deployment.save()

        # create resource
        resource_resp = self.api_gateway.create_resource(
            restApiId=self.deployment.config['rest_api_id'],
            pathPart=self.deployment.name
        )

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
            "lambda-function-name": self.deployment.name,
        }

        uri = "arn:aws:apigateway:{aws-region}:lambda:path/{api-version}/functions/arn:aws:lambda:{aws-region}:{aws-acct-id}:function:{lambda-function-name}/invocations".format(**uri_data)

        # create integration
        self.api_gateway.put_integration(
            restApiId=self.deployment.config['rest_api_id'],
            resourceId=resource_resp['id'],
            httpMethod="GET",
            type="AWS",
            integrationHttpMethod="POST",
            uri=uri,
        )

        self.api_gateway.put_integration_response(
            restApiId=self.deployment.config['rest_api_id'],
            resourceId=resource_resp['id'],
            httpMethod="POST",
            statusCode="200",
            selectionPattern=".*"
        )

        # create POST method response
        self.api_gateway.put_method_response(
            restApiId=self.deployment.config['rest_api_id'],
            resourceId=resource_resp['id'],
            httpMethod="GET",
            statusCode="200",
        )

        uri_data['aws-api-id'] = self.deployment.config['rest_api_id']
        source_arn = "arn:aws:execute-api:{aws-region}:{aws-acct-id}:{aws-api-id}/*/GET/{lambda-function-name}".format(**uri_data)

        self.lmbd.add_permission(
            FunctionName=self.deployment.name,
            StatementId=uuid.uuid4().hex,
            Action="lambda:InvokeFunction",
            Principal="apigateway.amazonaws.com",
            SourceArn=source_arn
        )

        # state 'your stage name' was already created via API Gateway GUI
        self.api_gateway.create_deployment(
            restApiId=self.deployment.config['rest_api_id'],
            stageName=self.deployment.stage,
        )

    def create_project_api(self):
        resp = self.api_gateway.create_rest_api(
            name=self.deployment.project.name,
        )
        self.development.config['rest_api_id'] = resp['id']

    def prepare_package(self):
        framework_file = requests.get(self.deployment.framework.url, stream=True)
        package = zipfile.ZipFile(io.BytesIO(framework_file.content))
        join = partial(os.path.join, self.deployment.volume_path)
        for user_file in self.deployment.config['files']:
            package.write(join(user_file))
        return base64.base64encode(package.fp.read())
