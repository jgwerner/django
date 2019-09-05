### Environment Variables Explanation

The IllumiDesk `app-backend` application interacts with various internal applications and external, third-party services. The following descriptions should help to understand the most important of these variables:

| Variable  |  Type | Note  | Default Value |
|---|---|---|---|
| API_HOST |<string> | API host either as IPv4 or FQDN. | `dev-api.illumidesk.com` |
| API_PORT |<string> | API port. | `443` |
| AWS_ACCOUNT_ID | <string> | AWS account ID | `860100747351` |
| AWS_SES_ACCESS_KEY_ID |<string> | Pair with AWS_SES_SECRET_ACCESS_KEY to access Simple Email Service (SES) | `''` |
| AWS_SES_SECRET_ACCESS_KEY | <string> | Pair with AWS_SES_ACCESS_KEY_ID to access Simple Email Service (SES) | `''` |
| AWS_SES_REGION_NAME | <string> | Name of AWS SES region, a geographic area containing Amazon data centers | `''` |
| AWS_SES_REGION_ENDPOINT | <string> | API endpoint associated with AWS_SES_REGION_NAME | `''` |
| AWS_ACCESS_KEY_ID | <string> | User account ID key to access general Amazon Web Services (AWS) | `''` |
| AWS_SECRET_ACCESS_KEY | <string> | Secret key associated with AWS_ACCESS_KEY_ID | `''` |
| AWS_DEFAULT_REGION | <string> | Default region for AWS access | `''` |
| DEBUG | <boolean> | Enables the app's debug mode | `True` |
| DEFAULT_FROM_EMAIL | <email> | Default email address for sending app-backend messages | `no-reply@illumidesk.com` |
| DJANGO_SETTINGS_MODULE | <string> | Module name of Django application settings file | `config.settings.dev` |
| DOCKER_NET | <string> | Used to allow workspace containers with docker-compose, used only to run tests. | `illumidesk` |
| ECS_CLUSTER | <string> | Name of Elastic Container Service (ECS) Cluster | `default` |
| EMAIL_HOST | <string> | Host address for email client | `localhost` |
| EMAIL_PORT | <integer> | Port number for email client | `587` |
| EMAIL_HOST_USER | <string> | Email host username | `''` |
| EMAIL_HOST_PASSWORD | <string> | Password associated with EMAIL_HOST_USER | `''` |
| EXCHANGE_DIR_CONTAINER | <string> | Exchange directory used by `nbgrader` to exchange files. | `/srv/nbgrader/exchange` |
| EXCHANGE_DIR_HOST | <string> | Exchange directory used by `nbgrader` to exchange files. | `/workspaces/nbgrader/exchange` |
| EXTERNAL_IPV4 | <string> | External facing IPV4 address included with ALLOWED_HOSTS. | `''` |
| FRONTEND_DOMAIN | <string> | Frontend domain name. | `dev-app.illumidesk.com` |
| REDIS_URL | <string> | URL for Redis data store/notifications | `redis://localhost:6379/0` |
| RESOURCE_DIR | <string> | Root level directory for all user directories | `/workspaces` |
| SECRET_KEY | <string> | Secret key used for Django-related security | `''` |
| SENTRY_DSN | <string> | Data Source Name (DSN) for Sentry's error tracking and monitoring service | `''` |
| SERVER_RESOURCE_DIR | <string> | Container user home folder. | `/home/jovyan` |
| SITE_ID | <string> | Site ID as UUID | `c66d1616-09a7-4594-8c6d-2e1c1ba5fe3b` |
| TLS | <boolean> | Enables application's use of secure HTTP | `False` |