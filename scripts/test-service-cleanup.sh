#!/bin/bash

# Test script for Zeabur service cleanup (for PR review app cleanup)
# Usage: ./scripts/test-service-cleanup.sh

set -e

echo "🧹 Testing Zeabur Service Cleanup..."

# Check if fzf is installed
if ! command -v fzf &> /dev/null; then
    echo "❌ fzf is not installed. Please install it first."
    echo "On macOS: brew install fzf"
    echo "On Ubuntu: sudo apt install fzf"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "❌ jq is not installed. Please install it first."
    echo "On macOS: brew install jq"
    echo "On Ubuntu: sudo apt install jq"
    exit 1
fi

# Check if yq is installed
if ! command -v yq &> /dev/null; then
    echo "❌ yq is not installed. Please install it first."
    echo "On macOS: brew install yq"
    echo "On Ubuntu: sudo snap install yq"
    exit 1
fi

# Get API key from zeabur CLI config
if [ -f ~/.config/zeabur/cli.yaml ]; then
    API_KEY=$(yq '.token' ~/.config/zeabur/cli.yaml)
    if [ "$API_KEY" = "null" ] || [ -z "$API_KEY" ]; then
        echo "❌ No API key found in ~/.config/zeabur/cli.yaml"
        echo "Please login with: zeabur auth login"
        exit 1
    fi
else
    echo "❌ Zeabur CLI config not found at ~/.config/zeabur/cli.yaml"
    echo "Please install Zeabur CLI and login: zeabur auth login"
    exit 1
fi

echo "✅ API key found in CLI config"

# Test API connection
echo "🔍 Testing API connection..."

RESPONSE=$(curl -s --request POST \
  --url https://api.zeabur.com/graphql \
  --header "Authorization: Bearer $API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{"query":"query { me { username } }"}')

USERNAME=$(echo "$RESPONSE" | jq -r '.data.me.username')
if [ "$USERNAME" = "null" ] || [ -z "$USERNAME" ]; then
    echo "❌ Failed to authenticate with API"
    exit 1
fi

echo "✅ API connection successful! Logged in as: $USERNAME"

# Fetch available projects
echo "📋 Fetching your projects..."

PROJECTS_RESPONSE=$(curl -s --request POST \
  --url https://api.zeabur.com/graphql \
  --header "Authorization: Bearer $API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{"query":"query { projects { edges { node { _id name } } } }"}')

# Check for errors
if echo "$PROJECTS_RESPONSE" | jq -e '.errors' > /dev/null; then
    echo "❌ Failed to fetch projects:"
    echo "$PROJECTS_RESPONSE" | jq '.errors'
    exit 1
fi

# Extract projects and use fzf for selection
PROJECTS_LIST=$(echo "$PROJECTS_RESPONSE" | jq -r '.data.projects.edges[] | "\(.node._id) - \(.node.name)"')

if [ -z "$PROJECTS_LIST" ]; then
    echo "❌ No projects found. Please create a project first."
    exit 1
fi

echo "🔍 Select a project using fzf:"
SELECTED_PROJECT=$(echo "$PROJECTS_LIST" | fzf --prompt="Select project: " --height=10)
if [ -z "$SELECTED_PROJECT" ]; then
    echo "ℹ️  No project selected. Exiting..."
    exit 0
fi

PROJECT_ID=$(echo "$SELECTED_PROJECT" | cut -d' ' -f1)
PROJECT_NAME=$(echo "$SELECTED_PROJECT" | cut -d' ' -f3-)

echo "✅ Selected project: $PROJECT_NAME ($PROJECT_ID)"

# Fetch services for the selected project
echo "🔍 Fetching services for project: $PROJECT_NAME"

SERVICES_RESPONSE=$(curl -s --request POST \
  --url https://api.zeabur.com/graphql \
  --header "Authorization: Bearer $API_KEY" \
  --header 'Content-Type: application/json' \
  --data "{\"query\":\"query Services(\$projectId: ObjectID) { services(projectID: \$projectId) { edges { node { name _id } } } }\", \"variables\": {\"projectId\": \"$PROJECT_ID\"}}")

echo "Services API Response:"
echo "$SERVICES_RESPONSE" | jq .

# Check for errors
if echo "$SERVICES_RESPONSE" | jq -e '.errors' > /dev/null; then
    echo "❌ Failed to fetch services:"
    echo "$SERVICES_RESPONSE" | jq '.errors'
    exit 1
fi

# Extract services
SERVICES_LIST=$(echo "$SERVICES_RESPONSE" | jq -r '.data.services.edges[] | "\(.node._id) - \(.node.name)"')

if [ -z "$SERVICES_LIST" ]; then
    echo "ℹ️  No services found in this project."
    exit 0
fi

echo ""
echo "📋 Available services:"
echo "$SERVICES_LIST"

echo ""
echo "🔍 Select services to delete using fzf (use TAB for multi-select, ENTER to confirm):"
echo "⚠️  WARNING: This will permanently delete the selected services!"

# Use fzf with multi-select capability
SELECTED_SERVICES=$(echo "$SERVICES_LIST" | fzf --multi --prompt="Select services to delete: " --height=15 --header="Use TAB to select multiple services, ENTER to confirm")

if [ -z "$SELECTED_SERVICES" ]; then
    echo "ℹ️  No services selected. Exiting..."
    exit 0
fi

echo ""
echo "📋 Selected services for deletion:"
echo "$SELECTED_SERVICES"

echo ""
read -p "⚠️  Are you sure you want to delete these services? This action cannot be undone! (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "ℹ️  Service deletion cancelled."
    exit 0
fi

echo ""
echo "🗑️  Deleting selected services..."

# Process each selected service
echo "$SELECTED_SERVICES" | while IFS= read -r service_line; do
    SERVICE_ID=$(echo "$service_line" | cut -d' ' -f1)
    SERVICE_NAME=$(echo "$service_line" | cut -d' ' -f3-)
    
    echo "🗑️  Deleting service: $SERVICE_NAME ($SERVICE_ID)"
    
    DELETE_RESPONSE=$(curl -s --request POST \
      --url https://api.zeabur.com/graphql \
      --header "Authorization: Bearer $API_KEY" \
      --header 'Content-Type: application/json' \
      --data "{\"query\":\"mutation deleteService(\$id: ObjectID!) { deleteService(_id: \$id) }\", \"variables\": {\"id\": \"$SERVICE_ID\"}}")
    
    echo "Delete response for $SERVICE_NAME:"
    echo "$DELETE_RESPONSE" | jq .
    
    # Check for errors
    if echo "$DELETE_RESPONSE" | jq -e '.errors' > /dev/null; then
        echo "❌ Failed to delete service $SERVICE_NAME:"
        echo "$DELETE_RESPONSE" | jq '.errors'
    else
        DELETE_SUCCESS=$(echo "$DELETE_RESPONSE" | jq -r '.data.deleteService')
        if [ "$DELETE_SUCCESS" = "true" ]; then
            echo "✅ Successfully deleted service: $SERVICE_NAME"
        else
            echo "❌ Failed to delete service: $SERVICE_NAME (returned false)"
        fi
    fi
    
    echo ""
done

echo "🎉 Service cleanup test completed!"
echo "ℹ️  Check your Zeabur dashboard to verify the services were deleted."