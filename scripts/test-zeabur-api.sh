#!/bin/bash

# Test script for Zeabur API connection
# Usage: ./scripts/test-zeabur-api.sh

set -e

echo "🔧 Testing Zeabur API Connection..."

# Check if yq is installed
if ! command -v yq &> /dev/null; then
    echo "❌ yq is not installed. Please install it first."
    echo "On macOS: brew install yq"
    echo "On Ubuntu: sudo snap install yq"
    exit 1
fi

# Check if jq is installed
if ! command -v jq &> /dev/null; then
    echo "❌ jq is not installed. Please install it first."
    echo "On macOS: brew install jq"
    echo "On Ubuntu: sudo apt install jq"
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

# Test API connection with simple query
echo "🔍 Testing API connection..."

RESPONSE=$(curl -s --request POST \
  --url https://api.zeabur.com/graphql \
  --header "Authorization: Bearer $API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{"query":"query { me { username } }"}')

echo "API Response:"
echo "$RESPONSE" | jq .

# Check if the response contains errors
if echo "$RESPONSE" | jq -e '.errors' > /dev/null; then
    echo "❌ API test failed with errors:"
    echo "$RESPONSE" | jq '.errors'
    exit 1
fi

# Extract username
USERNAME=$(echo "$RESPONSE" | jq -r '.data.me.username')
if [ "$USERNAME" = "null" ] || [ -z "$USERNAME" ]; then
    echo "❌ Failed to get username from API"
    exit 1
fi

echo "✅ API connection successful! Logged in as: $USERNAME"

# Test zeabur.yaml parsing
echo "🔧 Testing zeabur.yaml parsing..."

if [ ! -f "zeabur.yaml" ]; then
    echo "❌ zeabur.yaml not found in current directory"
    exit 1
fi

# Generate test template with PR number 999
echo "📝 Generating test template..."

# Remove the worker service (commented out anyway)
yq eval 'del(.spec.services[] | select(.name == "Disfactory Worker"))' zeabur.yaml > temp-test-zeabur.yaml

# Add PR number postfix to service names (process each service individually)
yq eval -i '.spec.services[0].name = .spec.services[0].name + "-pr-999"' temp-test-zeabur.yaml
yq eval -i '.spec.services[1].name = .spec.services[1].name + "-pr-999"' temp-test-zeabur.yaml

# Manually update dependencies for the backend service (index 1)
yq eval -i '.spec.services[1].dependencies[0] = "PostgreSQL-pr-999"' temp-test-zeabur.yaml

# Update template metadata for the review app
yq eval -i '.metadata.name = "Disfactory PR #999 (TEST)"' temp-test-zeabur.yaml
yq eval -i '.spec.description = "Test review app for PR #999"' temp-test-zeabur.yaml

# Keep the original domain variable key (BACKEND_DOMAIN)
# No need to change .spec.variables[0].key - keep it as BACKEND_DOMAIN
# Keep the original domainKey reference in the service

echo "✅ Test template generated successfully"
echo "📄 Generated template preview (first 50 lines):"
/bin/cat temp-test-zeabur.yaml | head -50

echo ""
echo "📄 Service names in generated template:"
yq eval '.spec.services[].name' temp-test-zeabur.yaml

echo ""
echo "📄 Template metadata:"
yq eval '.metadata.name' temp-test-zeabur.yaml
yq eval '.spec.description' temp-test-zeabur.yaml

# Ask user if they want to deploy
echo ""
read -p "🚀 Do you want to deploy this test template to Zeabur? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "ℹ️  Test template generation completed. Cleaning up..."
    rm -f temp-test-zeabur.yaml
    exit 0
fi

echo "🚀 Deploying test template to Zeabur..."

# Fetch available projects and let user select
echo "📋 Fetching your projects..."

PROJECTS_RESPONSE=$(curl -s --request POST \
  --url https://api.zeabur.com/graphql \
  --header "Authorization: Bearer $API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{"query":"query { projects { edges { node { _id name } } } }"}')

echo "Projects API Response:"
echo "$PROJECTS_RESPONSE" | jq .

# Check for errors
if echo "$PROJECTS_RESPONSE" | jq -e '.errors' > /dev/null; then
    echo "❌ Failed to fetch projects:"
    echo "$PROJECTS_RESPONSE" | jq '.errors'
    rm -f temp-test-zeabur.yaml
    exit 1
fi

# Extract projects and use fzf for selection
PROJECTS_LIST=$(echo "$PROJECTS_RESPONSE" | jq -r '.data.projects.edges[] | "\(.node._id) - \(.node.name)"')

if [ -z "$PROJECTS_LIST" ]; then
    echo "❌ No projects found. Please create a project first."
    rm -f temp-test-zeabur.yaml
    exit 1
fi

echo "Available projects:"
echo "$PROJECTS_LIST"

# Check if fzf is available
if command -v fzf &> /dev/null; then
    echo "🔍 Select a project using fzf:"
    SELECTED_PROJECT=$(echo "$PROJECTS_LIST" | fzf --prompt="Select project: " --height=10)
    if [ -z "$SELECTED_PROJECT" ]; then
        echo "ℹ️  No project selected. Exiting..."
        rm -f temp-test-zeabur.yaml
        exit 0
    fi
    PROJECT_ID=$(echo "$SELECTED_PROJECT" | cut -d' ' -f1)
else
    echo "📝 fzf not found. Please enter the project ID manually:"
    echo "$PROJECTS_LIST"
    read -p "Enter project ID: " PROJECT_ID
    if [ -z "$PROJECT_ID" ]; then
        echo "❌ No project ID provided. Exiting..."
        rm -f temp-test-zeabur.yaml
        exit 1
    fi
fi

echo "✅ Selected project ID: $PROJECT_ID"

# Use generated domain name directly (no availability check needed)
DOMAIN_NAME="disfactory-pr-999-test"
echo "📝 Using generated domain: $DOMAIN_NAME.zeabur.app"

TEMPLATE_CONTENT=$(cat temp-test-zeabur.yaml)

# Escape the template content for JSON
ESCAPED_TEMPLATE=$(echo "$TEMPLATE_CONTENT" | jq -Rs .)

# Prepare the GraphQL mutation (matching actual API client)
MUTATION=$(cat <<EOF
{
  "query": "mutation DeployTemplate(\$rawSpecYaml: String, \$variables: Map, \$projectID: ObjectID) { deployTemplate(rawSpecYaml: \$rawSpecYaml, variables: \$variables, projectID: \$projectID) { _id name region { id } } }",
  "variables": {
    "rawSpecYaml": $ESCAPED_TEMPLATE,
    "variables": {
      "BACKEND_DOMAIN": "$DOMAIN_NAME"
    },
    "projectID": "$PROJECT_ID"
  }
}
EOF
)

DEPLOY_RESPONSE=$(curl -s --request POST \
  --url https://api.zeabur.com/graphql \
  --header "Authorization: Bearer $API_KEY" \
  --header "Content-Type: application/json" \
  --data "$MUTATION")

echo "🔍 Deployment Response:"
echo "$DEPLOY_RESPONSE" | jq .

# Check for errors
if echo "$DEPLOY_RESPONSE" | jq -e '.errors' > /dev/null; then
    echo "❌ Deployment failed with errors:"
    echo "$DEPLOY_RESPONSE" | jq '.errors'
    rm -f temp-test-zeabur.yaml
    exit 1
fi

# Extract deployment info
PROJECT_NAME=$(echo "$DEPLOY_RESPONSE" | jq -r '.data.deployTemplate.name')
DEPLOYED_PROJECT_ID=$(echo "$DEPLOY_RESPONSE" | jq -r '.data.deployTemplate._id')
REGION_ID=$(echo "$DEPLOY_RESPONSE" | jq -r '.data.deployTemplate.region.id')

echo "✅ Test deployment successful!"
echo "📋 Project Name: $PROJECT_NAME"
echo "🆔 Project ID: $DEPLOYED_PROJECT_ID"
echo "🌍 Region: $REGION_ID"
echo "🔗 Review App URL: https://disfactory-pr-999-test.zeabur.app"

# Clean up
rm -f temp-test-zeabur.yaml

echo ""
echo "🎉 Zeabur API test completed successfully!"
echo "ℹ️  You can now use the GitHub Action to deploy review apps automatically."
echo "⚠️  Remember to clean up the test deployment manually from Zeabur dashboard if needed."
