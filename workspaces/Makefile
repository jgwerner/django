.PHONY: help
# Docker image name and tag. Build assumes ACCOUNT is set
# as an env var before running any commands.
OWNER?=$(ACCOUNT)
IMAGE?=$(DOCKER_IMAGE)
NAMESPACE:=$(OWNER)/$(DOCKER_IMAGE)
TAG?=latest
SHELL:=bash

ALL_STACKS:=minimal-notebook \
        datascience-notebook

ALL_IMAGES:=$(ALL_STACKS)

help:
# http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@echo "==========================="
	@echo "IllumiDesk workspace images"
	@echo "==========================="
	@echo ""
	@echo "Replace '%' with a stack directory name. The build command will add "
	@echo "the owner name and a tag to the image name (e.g. 'make build/datascience-notebook'"
	@echo "will create make 'acmeinc/datascience-notebook:latest')."
	@echo
	@grep -E '^[a-zA-Z0-9_%/-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

build/%: DARGS?=
build/%: ## Build and tag a stack
	docker build $(DARGS) --rm --force-rm -t $(OWNER)/$(notdir $@):$(TAG) ./$(notdir $@)

build-all: $(foreach I,$(ALL_IMAGES), build/$(I) ) ## Build all stacks
build-test-all: $(foreach I,$(ALL_IMAGES),build/$(I) test/$(I) ) ## build and test all stacks

test/%: ## run tests against a stack
	@TEST_IMAGE="$(OWNER)/$(notdir $@)" py.test --nbval test
test-all: $(foreach I,$(ALL_IMAGES), test/$(I) ) ## test all stacks

dev/%: ARGS?=
dev/%: DARGS?=
dev/%: PORT?=8080
dev/%: ## Make a container from a tagged image
	docker run -it --rm -p $(PORT):8080 $(DARGS) $(OWNER)/$(notdir $@) $(ARGS)

dev-env: ## Install libraries required to run containers and tests
	pip install -r requirements-dev.txt

push/%: ## Push an image to the registry
	docker push $(OWNER)/$(notdir $@):$(TAG)

push-all: $(foreach I,$(ALL_IMAGES), push/$(I) ) ## Push all stacks