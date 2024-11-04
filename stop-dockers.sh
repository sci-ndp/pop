#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if 'docker compose' is available, otherwise use 'docker-compose'
if command_exists "docker compose"; then
    DOCKER_COMPOSE="docker compose"
elif command_exists "docker-compose"; then
    DOCKER_COMPOSE="docker-compose"
else
    # echo "Error: Neither 'docker compose' nor 'docker-compose' found."
    DOCKER_COMPOSE="docker compose"
    # exit 1
fi

$DOCKER_COMPOSE down

$DOCKER_COMPOSE down --volumes --remove-orphans

docker image prune -f
