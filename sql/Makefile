# Magic Makefile Help
.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -e "^[a-zA-Z_\-]*: *.*## *" | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# Variables
# ---------
APP_NAME = churn-psql
REGISTRY_HOST = docker
DOCKER_REPO = dannyma
VERSION = 1.0.0

# Docker Tasks
# ------------
prune: ## Clear out Docker volumes
	docker system prune -f --all

build-nc: ## Build the container without caching
	docker build --no-cache -t $(APP_NAME) .

run: build-nc ## Run container
	docker run -i -t --rm --name="$(APP_NAME)" $(APP_NAME) $(task)

stop: ## Stop container
	docker kill $(APP_NAME) || true

up-local: ## Spin up docker compose locally
	docker-compose -f docker-compose.debug.yml up --force-recreate -d

down-local: ## Shutdown docker compose locally
	docker-compose -f docker-compose.debug.yml down -v --rmi local --remove-orphans

up: ## Spin up docker compose
	docker-compose up --force-recreate -d

down: ## Shutdown docker compose
	docker-compose down -v --remove-orphans

# Docker tagging
tag: tag-latest tag-version ## Generate container tags for the `{version}` ans `latest` tags

tag-latest: ## Generate container `{version}` tag
	@echo 'create tag latest'
	docker tag $(APP_NAME) $(DOCKER_REPO)/$(APP_NAME):latest

tag-version: ## Generate container `latest` tag
	@echo 'create tag $(VERSION)'
	docker tag $(APP_NAME) $(DOCKER_REPO)/$(APP_NAME):$(VERSION)

push: ## Push container to registry
	docker push $(DOCKER_REPO)/$(APP_NAME)