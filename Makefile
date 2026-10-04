# Docker Compose v2 plugin (`docker compose`, not the old `docker-compose`)
DOCKER_COMPOSE := docker compose

.PHONY: build run stop test clean

# Build target
build:
	$(DOCKER_COMPOSE) build

# Run target
run:
	$(DOCKER_COMPOSE) up -d

# Stop target
stop:
	$(DOCKER_COMPOSE) down

# Test target (needs: pip install -r requirements-dev.txt)
test:
	python -m pytest

# Clean target
clean: stop
	$(DOCKER_COMPOSE) rm -f
	docker system prune -f
