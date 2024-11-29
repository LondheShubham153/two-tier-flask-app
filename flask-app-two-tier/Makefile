# Determine the operating system
OS := $(shell uname)

# Define Docker compose command
DOCKER_COMPOSE := docker-compose

# Define Docker compose service name
SERVICE_NAME := web

# Build target
build:
ifeq ($(OS),Linux)
	@echo "Building for Linux"
	$(DOCKER_COMPOSE) build
endif
ifeq ($(OS),Darwin)
	@echo "Building for macOS"
	$(DOCKER_COMPOSE) build
endif
ifeq ($(OS),Windows_NT)
	@echo "Building for Windows"
	# Add Windows-specific build commands if you wish :P
endif

# Run target
run:
ifeq ($(OS),Linux)
	@echo "Running for Linux"
	$(DOCKER_COMPOSE) up -d
endif
ifeq ($(OS),Darwin)
	@echo "Running for macOS"
	$(DOCKER_COMPOSE) up -d
endif
ifeq ($(OS),Windows_NT)
	@echo "Running for Windows"
	# Add Windows-specific run commands if you wish :P
endif

# Stop target
stop:
	$(DOCKER_COMPOSE) down

# Clean target
clean: stop
	$(DOCKER_COMPOSE) rm -f
	docker system prune -f

