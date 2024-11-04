#!/bin/bash

# Function to check if 'docker compose' works
command_exists() {
    if docker compose version >/dev/null 2>&1; then
        return 0
    elif docker-compose version >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if 'docker compose' is available, otherwise use 'docker-compose'
if docker compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version >/dev/null 2>&1; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "Error: Neither 'docker compose' nor 'docker-compose' found."
    exit 1
fi

# Start docker compose
$DOCKER_COMPOSE up -d
