.PHONY: docs help changelog release

include app-backend/.env

# Terraform settings.
SRC = $(wildcard *.tf ./*/*.tf)
platform := $(shell uname)
pydeps := pyyaml boto3
modules = $(shell ls -1 ./*.tf ./*/*.tf | xargs -I % dirname %)

# Docker image name and tag. Build assumes ACCOUNT is set
# as an env var before running any commands.
ALL_APP-BACKEND_IMAGES:=app-backend
ALL_PROXY_IMAGES:=nginx \
        traefik
ALL_WORKSPACE_IMAGES:=datascience-notebook
AWS_ACCOUNT?=$(AWS_ACCOUNT)
AWS_REGION?=$(AWS_REGION)
DOCKER_NET?=$(DOCKER_NET)
OWNER_NAME?=$(OWNER_NAME)
SHELL:=bash
TAG?=latest

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@echo "=============================================="
	@echo "IllumiDesk make commands"
	@echo "=============================================="
	@echo ""
	@echo "Set environment variables:"
	@echo ""
	@echo "AWS_ACCOUNT: AWS account number"
	@echo "AWS_REGION: AWS region"
	@echo "DOCKER_NET: Docker network name"
	@echo "OWNER_NAME: Owner name, used to define image namespace in registry"
	@echo "TAG: Docker image tag"
	@echo ""
	@echo "Build images:"
	@echo "____________"
	@echo ""
	@echo "To build an image, use the 'build-*' prefix and replace % with a stack directory name,"
	@echo "where '*' is the stack name (e.g., make build-workspace/datascience-notebook)."
	@echo ""
	@echo "To build all images for a stack, use the 'build-all-*' prefix, where '*' is one of app-backend, proxies, or workspaces."
	@echo ""
	@echo "Push images:"
	@echo "___________"
	@echo ""
	@echo "To push an image to the registry, use the 'prefix-*' prefix and replace % with a stack directory name"
	@echo "where '*' is the stack name (e.g., make push-workspace/datascience-notebook)."
	@echo ""
	@grep -E '^[a-zA-Z0-9_%/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Create docker network
docker-network: ## Create docker network if it doesn't exit
	@docker network inspect $(DOCKER_NET) >/dev/null 2>&1 || docker network create $(DOCKER_NET)

# Changelog and release: https://github.com/conventional-changelog/standard-version
release: ## Create a new minor release
	npm run release -- --release-as minor

destroy: ## Remove all docker containers, volumes, and networks
	docker rm -f `docker ps -aq`
	docker volume prune -f
	docker network rm $(DOCKER_NET)

# Build and push proxy servers
build-proxy/%: DARGS?=
build-proxy/%: ## Build and tag a reverse-proxy image
	docker build $(DARGS) --rm --force-rm -t $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(OWNER_NAME)/$(notdir $@):$(TAG) ./reverse-proxies/$(notdir $@)

build-all-proxies: $(foreach I,$(ALL_PROXY_IMAGES), build-proxy/$(I) ) ## Build and tag all reverse-proxy images

push-proxy/%: ## Push a reverse-proxy image to the registry
	docker push $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(OWNER_NAME)/$(notdir $@):$(TAG)

push-all-proxies: $(foreach I,$(ALL_PROXY_IMAGES), push-proxy/$(I) ) ## Push all reverse-proxy images to the registry

# Build and push app-backend image (Django based services)
build-app-backend/%: DARGS?=
build-app-backend/%: ## Build and tag an app-backend image
	docker build $(DARGS) --rm --force-rm -t $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(OWNER_NAME)/$(notdir $@):$(TAG) ./$(notdir $@)
build-all-backends: $(foreach I,$(ALL_APP-BACKEND_IMAGES), build-app-backend/$(I) ) ## Build and tag all app-backend images

push-app-backend/%: ## Push an app-backend image to the registry
	docker push $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(OWNER_NAME)/$(notdir $@):$(TAG)
push-all-backends: $(foreach I,$(APP-BACKEND_IMAGES), push-app-backend/$(I) ) ## Push all app-backend images to the registry

# Build and push workspaces (Jupyter Notebooks)
build-workspace/%: DARGS?=
build-workspace/%: ## Build and tag a workspace image
	docker build $(DARGS) --rm --force-rm -t $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(OWNER_NAME)/$(notdir $@):$(TAG) ./workspaces/$(notdir $@)

build-all-workspaces: $(foreach I,$(ALL_WORKSPACE_IMAGES), build-workspace/$(I) ) ## Build and tag all workspace images

push-workspace/%: ## Push a workspace image to the registry
	docker push $(AWS_ACCOUNT).dkr.ecr.$(AWS_REGION).amazonaws.com/$(OWNER_NAME)/$(notdir $@):$(TAG)

push-all-workspaces: $(foreach I,$(ALL_WORKSPACE_IMAGES), push-workspace/$(I) ) ## Push all workspace images to the registry
