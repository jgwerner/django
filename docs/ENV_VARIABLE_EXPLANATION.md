### Environment Variables Explanation

The IllumiDesk/app-backend application interacts with various internal applications and external, third-party services. The following descriptions should help to understand the most important of these variables:

| Variable  |  Type | Note  |
|---|---|---|
| AWS_SES_ACCESS_KEY_ID |<string> | Pair with AWS_SES_SECRET_ACCESS_KEY to access Simple Email Service (SES) |
| AWS_SES_SECRET_ACCESS_KEY | <string> | Pair with AWS_SES_ACCESS_KEY_ID to access Simple Email Service (SES) |
| AWS_SES_REGION_NAME | <string> | Name of AWS SES region, a geographic area containing Amazon data centers |
| AWS_SES_REGION_ENDPOINT | <string> | API endpoint associated with AWS_SES_REGION_NAME |
| AWS_ACCESS_KEY_ID | <string> | User account ID key to access general Amazon Web Services (AWS) |
| AWS_SECRET_ACCESS_KEY | <string> | Secret key associated with AWS_ACCESS_KEY_ID |
| AWS_DEFAULT_REGION | <string> | Default region for AWS access |
| ECS_CLUSTER | <string> | Name of Elastic Container Service (ECS) Cluster |
| AWS_STORAGE_BUCKET_NAME | <string> | Your AWS storage bucket name |
| AWS_S3_CUSTOM_DOMAIN | <string> | Domain of S3, if used as a Content Delivery Network (CDN) |
| DATABASE_HOST=localhost | <string> | Database host |
| DATABASE_USER=postgres | <string> | Database user |
| DATABASE_PASSWORD | <string> | Database password |
| DATABASE_PORT | <string> | Database port |
| DATABASE_NAME | <string> | Database name |
| DEBUG | <boolean> | Enables the app's debug mode |
| DEFAULT_FROM_EMAIL | <email> | Default email address for sending app-backend messages |
| DEFAULT_STRIPE_PLAN_ID | <string> | Name of Stripe subscription plan (also the default for new users) |
| DJANGO_SETTINGS_MODULE | <string> | Module name of Django application settings file |
| DOCKER_DOMAIN | <string> | IP address of your Docker's domain |
| DOCKER_HOST | <string> | TCP address of your Docker's host |
| DOCKER_EVENTS_URL | <string> | URL for your Docker's events distributor |
| DOCKER_NET | <string> | Name of Docker Net |
| ELASTICSEARCH_URL | <string> | URL for Elasticsearch endpoint |
| ELASTICSEARCH_USER | <string> | Elasticsearch username |
| ELASTICSEARCH_PASSWORD | <string> | Password associated with ELASTICSEARCH_USER |
| EMAIL_HOST | <string> | Host address for email client |
| EMAIL_PORT | <integer> | Port number for email client |
| EMAIL_HOST_USER | <string> | Email host username |
| EMAIL_HOST_PASSWORD | <string> | Password associated with EMAIL_HOST_USER |
| EMAIL_USE_TLS | <boolean> | Enables Transport Layer Security (TLS) when talking to SMTP server |
| EMAIL_USE_SSL | <boolean> | Enables implicit TLS (commonly known as "SSL") when talking to SMTP server |
| EXTERNAL_IPV4 | <string> | External facing IPV4 address, required by webapp to accept connections without a domain name. |
| GITHUB_CLIENT_ID | <string> | Client ID for Github account |
| GITHUB_CLIENT_SECRET | <string> | Secret access key associated with GITHUB_CLIENT_ID |
| GOOGLE_CLIENT_ID | <string> | Client ID for Google account |
| GOOGLE_CLIENT_SECRET | <string> | Secret access key associated with GOOGLE_CLIENT_ID |
| GETTING_STARTED_PROJECT | <string> | Name of "Getting Started" project |
| MOCK_STRIPE | <boolean> | Enables use of mock connections to Stripe for development purposes |
| NVIDIA_DOCKER_HOST | <string> | URL for NVIDIA Docker host |
| RABBITMQ_URL | <string> | URL for RabbitMQ message broker |
| REDIS_URL | <string> | URL for Redis data store/notifications |
| RESOURCE_DIR | <string> | Root level directory for all user directories |
| SECRET_KEY | <string> | Secret key used for Django-related security |
| SENTRY_DSN | <string> | Data Source Name (DSN) for Sentry's error tracking and monitoring service |
| SERVER_PORT | <integer> | Port number for main application environment |
| SERVER_RESOURCE_DIR | <string> | Name of relevant project's resource directory |
| SLACK_KEY | <string> | Slack account ID key |
| SLACK_SECRET | <string> | Secret access key associated with SLACK_KEY |
| STATIC_ROOT | <string> | Absolute path to the directory static files should be collected to. |
| STRIPE_SECRET_KEY | <string> | Secret key associated with Stripe payment information |
| APP_DOMAIN | <string> | Domain of IllumiDesk main development environment |
| APP_SCHEME | <string> | An additional host name or IP address from which the application will allow connections, added to Django's ALLOWED_HOSTS |
| TLS | <boolean> | Enables application's use of secure HTTP |
| TRAVIS_PULL_REQUEST | <boolean> | Enables Travis CI's automated Docker image building upon pull request submission |
