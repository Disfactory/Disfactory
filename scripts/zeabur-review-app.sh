#!/bin/bash

# Zeabur Review App Management Script
# Usage: ./scripts/zeabur-review-app.sh <action> [options]
# Actions: deploy, cleanup, status
#
# Environment variables required:
# - ZEABUR_API_KEY: Zeabur API token
# - ZEABUR_PROJECT_ID: Target project ID
# - PR_NUMBER: Pull request number
# - COMMIT_SHA: Git commit hash (optional, defaults to HEAD)
#
# Project-specific configuration (optional, with defaults):
# - PROJECT_NAME: Project name for review apps (default: "Review App")
# - IGNORED_SERVICES: Comma-separated list of service names to exclude from review apps (default: "")
# - CLEANUP_SERVICES: Comma-separated list of service names to clean up after deployment (default: "")
# - UPDATE_IMAGE_SERVICES: Comma-separated list of service name patterns to update with commit tags (default: "")
# - DOMAIN_PREFIX: Domain prefix for review apps (default: "app")
# - IMAGE_TAG_PREFIX: Image tag prefix (default: "sha")

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Configuration
API_URL="https://api.zeabur.com/graphql"
TEMPLATE_FILE="$PROJECT_ROOT/zeabur.yaml"
CONFIG_FILE="$PROJECT_ROOT/zeabur-config.env"

# Load project-specific configuration if available
if [ -f "$CONFIG_FILE" ]; then
    echo "ℹ️  Loading configuration from: $CONFIG_FILE"
    # shellcheck source=/dev/null
    source "$CONFIG_FILE"
fi

# Project-specific configuration with defaults
PROJECT_NAME="${PROJECT_NAME:-Review App}"
IGNORED_SERVICES="${IGNORED_SERVICES:-}"
CLEANUP_SERVICES="${CLEANUP_SERVICES:-}"
UPDATE_IMAGE_SERVICES="${UPDATE_IMAGE_SERVICES:-}"
DOMAIN_PREFIX="${DOMAIN_PREFIX:-app}"
IMAGE_TAG_PREFIX="${IMAGE_TAG_PREFIX:-sha}"

# Logging functions
log_info() { echo "ℹ️  $1"; }
log_success() { echo "✅ $1"; }
log_warning() { echo "⚠️  $1"; }
log_error() { echo "❌ $1"; }

# Check required tools
check_dependencies() {
    local missing_tools=()

    for tool in curl jq yq; do
        if ! command -v "$tool" &> /dev/null; then
            missing_tools+=("$tool")
        fi
    done

    if [ ${#missing_tools[@]} -ne 0 ]; then
        log_error "Missing required tools: ${missing_tools[*]}"
        log_info "Install them with:"
        log_info "  macOS: brew install ${missing_tools[*]}"
        log_info "  Ubuntu: sudo apt install ${missing_tools[*]}"
        exit 1
    fi
}

# Validate environment variables
validate_env() {
    local required_vars=("ZEABUR_API_KEY" "ZEABUR_PROJECT_ID" "PR_NUMBER")
    local missing_vars=()

    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done

    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Missing required environment variables: ${missing_vars[*]}"
        exit 1
    fi

    # Set default commit SHA if not provided
    if [ -z "$COMMIT_SHA" ]; then
        COMMIT_SHA=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
    fi

    # Truncate commit hash to 7 characters for consistency with image tags
    COMMIT_SHA="${COMMIT_SHA:0:7}"
}

# Make GraphQL API request
graphql_request() {
    local query="$1"
    local variables="$2"

    local payload
    if [ -n "$variables" ]; then
        payload=$(jq -n \
            --arg query "$query" \
            --argjson variables "$variables" \
            '{query: $query, variables: $variables}')
    else
        payload=$(jq -n --arg query "$query" '{query: $query}')
    fi

    curl -s --request POST \
        --url "$API_URL" \
        --header "Authorization: Bearer $ZEABUR_API_KEY" \
        --header "Content-Type: application/json" \
        --data "$payload"
}

# Generate unique service identifiers
get_service_suffix() {
    echo "pr-${PR_NUMBER}-${COMMIT_SHA}"
}

get_domain_name() {
    echo "${DOMAIN_PREFIX}-pr-${PR_NUMBER}-${COMMIT_SHA}"
}

# Generate modified template for review app
generate_template() {
    local suffix=$(get_service_suffix)
    local temp_template="$PROJECT_ROOT/temp-zeabur-pr-${PR_NUMBER}.yaml"

    # Start with the original template
    cp "$TEMPLATE_FILE" "$temp_template"

    # Remove ignored services if specified
    if [ -n "$IGNORED_SERVICES" ]; then
        IFS=',' read -ra IGNORED_ARRAY <<< "$IGNORED_SERVICES"
        for ignored_service in "${IGNORED_ARRAY[@]}"; do
            ignored_service=$(echo "$ignored_service" | xargs) # trim whitespace
            if [ -n "$ignored_service" ]; then
                log_info "Removing ignored service: $ignored_service"
                yq eval -i "del(.spec.services[] | select(.name | contains(\"$ignored_service\")))" "$temp_template"
            fi
        done
    fi

    # Update all service names with PR and commit suffix
    local service_count
    service_count=$(yq eval '.spec.services | length' "$temp_template")

    # Store original service names for dependency updates
    local original_services=()
    for i in $(seq 0 $((service_count - 1))); do
        local service_name
        service_name=$(yq eval ".spec.services[$i].name" "$temp_template")
        original_services+=("$service_name")
    done

    # Update service names
    for i in $(seq 0 $((service_count - 1))); do
        yq eval -i ".spec.services[$i].name = .spec.services[$i].name + \"-$suffix\"" "$temp_template"
    done

    # Update dependencies to match new service names
    for i in $(seq 0 $((service_count - 1))); do
        local deps_count
        deps_count=$(yq eval ".spec.services[$i].dependencies | length" "$temp_template" 2>/dev/null || echo "0")

        if [ "$deps_count" != "0" ] && [ "$deps_count" != "null" ]; then
            for j in $(seq 0 $((deps_count - 1))); do
                local dep_name
                dep_name=$(yq eval ".spec.services[$i].dependencies[$j]" "$temp_template")
                # Update dependency name to include suffix
                yq eval -i ".spec.services[$i].dependencies[$j] = \"$dep_name-$suffix\"" "$temp_template"
            done
        fi
    done

    # Update template metadata
    yq eval -i ".metadata.name = \"${PROJECT_NAME} PR #${PR_NUMBER} (${COMMIT_SHA})\"" "$temp_template"
    yq eval -i ".spec.description = \"Review app for PR #${PR_NUMBER} at commit ${COMMIT_SHA}\"" "$temp_template"

    # Update image tags with commit-specific versions
    local image_tag="${IMAGE_TAG_PREFIX}-${COMMIT_SHA}"

    # Update images for specified services
    if [ -n "$UPDATE_IMAGE_SERVICES" ]; then
        local service_count
        service_count=$(yq eval '.spec.services | length' "$temp_template")

        IFS=',' read -ra UPDATE_ARRAY <<< "$UPDATE_IMAGE_SERVICES"

        for i in $(seq 0 $((service_count - 1))); do
            local service_name current_image
            service_name=$(yq eval ".spec.services[$i].name" "$temp_template" 2>/dev/null || echo "")
            current_image=$(yq eval ".spec.services[$i].spec.source.image" "$temp_template" 2>/dev/null || echo "")

            if [ -n "$current_image" ] && [ "$current_image" != "null" ] && [ -n "$service_name" ]; then
                # Check if this service should have its image updated
                local should_update=false
                for update_pattern in "${UPDATE_ARRAY[@]}"; do
                    update_pattern=$(echo "$update_pattern" | xargs) # trim whitespace
                    if [ -n "$update_pattern" ] && [[ "$service_name" == *"$update_pattern"* ]]; then
                        should_update=true
                        break
                    fi
                done

                if [ "$should_update" = true ]; then
                    # Extract the base repository name and update with new tag
                    local base_repo
                    base_repo=$(echo "$current_image" | sed 's/:.*$//')
                    yq eval -i ".spec.services[$i].spec.source.image = \"${base_repo}:${image_tag}\"" "$temp_template"
                    log_info "Updated image for service '$service_name': ${base_repo}:${image_tag}"
                fi
            fi
        done
    fi

    # Return only the template path, no logging
    echo "$temp_template"
}

# Deploy review app
deploy_review_app() {
    log_info "Deploying review app for PR #${PR_NUMBER} (commit: ${COMMIT_SHA})"

    local suffix=$(get_service_suffix)
    log_info "Generating template with suffix: $suffix"

    local template_file=$(generate_template)
    local domain_name=$(get_domain_name)

    log_info "Generated template: $template_file"
    log_info "Domain name: $domain_name"
    log_info "Updating image tags to: sha-${COMMIT_SHA}"

    # Verify template file exists
    if [ ! -f "$template_file" ]; then
        log_error "Template file was not created: $template_file"
        exit 1
    fi

    # Read and escape template content
    local template_content
    template_content=$(cat "$template_file")
    local escaped_template
    escaped_template=$(echo "$template_content" | jq -Rs .)

    # Prepare GraphQL variables
    local variables
    variables=$(jq -n \
        --arg template "$template_content" \
        --arg domain "$domain_name" \
        --arg project_id "$ZEABUR_PROJECT_ID" \
        '{
            rawSpecYaml: $template,
            variables: {
                BACKEND_DOMAIN: $domain
            },
            projectID: $project_id
        }')

    # Deploy using GraphQL API
    local mutation='mutation DeployTemplate($rawSpecYaml: String, $variables: Map, $projectID: ObjectID) {
        deployTemplate(rawSpecYaml: $rawSpecYaml, variables: $variables, projectID: $projectID) {
            _id
            name
            region { id }
        }
    }'

    log_info "Sending deployment request..."
    local response
    response=$(graphql_request "$mutation" "$variables")

    log_info "API Response:"
    echo "$response" | jq .

    # Check for errors
    if echo "$response" | jq -e '.errors' > /dev/null; then
        log_error "Deployment failed:"
        echo "$response" | jq '.errors'
        rm -f "$template_file"
        exit 1
    fi

    # Extract deployment info
    local project_name project_id region_id
    project_name=$(echo "$response" | jq -r '.data.deployTemplate.name')
    project_id=$(echo "$response" | jq -r '.data.deployTemplate._id')
    region_id=$(echo "$response" | jq -r '.data.deployTemplate.region.id')

    log_success "Review app deployed successfully!"
    log_info "Project Name: $project_name"
    log_info "Project ID: $project_id"
    log_info "Region: $region_id"
    log_info "URL: https://${domain_name}.zeabur.app"

    # Clean up temporary file
    rm -f "$template_file"

    # Export results for GitHub Actions
    if [ -n "$GITHUB_ENV" ]; then
        echo "REVIEW_APP_URL=https://${domain_name}.zeabur.app" >> "$GITHUB_ENV"
        echo "REVIEW_APP_PROJECT_NAME=$project_name" >> "$GITHUB_ENV"
        echo "REVIEW_APP_PROJECT_ID=$project_id" >> "$GITHUB_ENV"
        echo "REVIEW_APP_REGION=$region_id" >> "$GITHUB_ENV"
        echo "REVIEW_APP_DOMAIN=$domain_name" >> "$GITHUB_ENV"
    fi

    # Wait for deployment readiness
    wait_for_deployment "https://${domain_name}.zeabur.app"

    # Clean up specified services after deployment
    cleanup_specified_services
}

# Clean up specified services after deployment
cleanup_specified_services() {
    if [ -z "$CLEANUP_SERVICES" ]; then
        log_info "No cleanup services specified, skipping post-deployment cleanup"
        return 0
    fi

    local suffix=$(get_service_suffix)
    log_info "Cleaning up specified services after deployment"

    # List services to find the cleanup targets
    local services_response
    services_response=$(list_services "$ZEABUR_PROJECT_ID")

    if echo "$services_response" | jq -e '.errors' > /dev/null; then
        log_warning "Failed to list services for cleanup:"
        echo "$services_response" | jq '.errors'
        return 1
    fi

    IFS=',' read -ra CLEANUP_ARRAY <<< "$CLEANUP_SERVICES"

    for cleanup_pattern in "${CLEANUP_ARRAY[@]}"; do
        cleanup_pattern=$(echo "$cleanup_pattern" | xargs) # trim whitespace
        if [ -z "$cleanup_pattern" ]; then
            continue
        fi

        local cleanup_service_name="${cleanup_pattern}-${suffix}"
        log_info "Looking for cleanup service: $cleanup_service_name"

        # Find the specific service to cleanup
        local service_id
        service_id=$(echo "$services_response" | jq -r --arg name "$cleanup_service_name" '
            .data.services.edges[] |
            select(.node.name == $name) |
            .node._id
        ')

        if [ -z "$service_id" ] || [ "$service_id" = "null" ]; then
            log_info "Cleanup service $cleanup_service_name not found or already removed"
            continue
        fi

        log_info "Found service to cleanup: $cleanup_service_name ($service_id)"

        # Delete the service
        local delete_response
        delete_response=$(delete_service "$service_id")

        if echo "$delete_response" | jq -e '.errors' > /dev/null; then
            log_warning "Failed to delete cleanup service $cleanup_service_name:"
            echo "$delete_response" | jq '.errors'
        else
            local delete_success
            delete_success=$(echo "$delete_response" | jq -r '.data.deleteService')
            if [ "$delete_success" = "true" ]; then
                log_success "Successfully cleaned up service: $cleanup_service_name"
            else
                log_warning "Failed to delete cleanup service: $cleanup_service_name (returned false)"
            fi
        fi
    done
}

# Wait for deployment to be ready
wait_for_deployment() {
    local url="$1"
    local max_attempts=30
    local wait_time=10

    log_info "Waiting for deployment to be ready: $url"

    for i in $(seq 1 $max_attempts); do
        if curl -sSf -o /dev/null "$url" 2>/dev/null || curl -sSf -o /dev/null "$url/admin/" 2>/dev/null; then
            log_success "Review app is ready!"
            return 0
        fi

        if [ $i -eq $max_attempts ]; then
            log_warning "Review app may still be starting up. Check manually: $url"
            return 1
        fi

        log_info "Attempt $i/$max_attempts: Service not ready yet, waiting ${wait_time}s..."
        sleep $wait_time
    done
}

# List services for a project
list_services() {
    local project_id="$1"

    local query='query Services($projectId: ObjectID) {
        services(projectID: $projectId) {
            edges {
                node {
                    name
                    _id
                }
            }
        }
    }'

    local variables
    variables=$(jq -n --arg project_id "$project_id" '{projectId: $project_id}')

    graphql_request "$query" "$variables"
}

# Delete a service
delete_service() {
    local service_id="$1"

    local mutation='mutation deleteService($id: ObjectID!) {
        deleteService(_id: $id)
    }'

    local variables
    variables=$(jq -n --arg id "$service_id" '{id: $id}')

    graphql_request "$mutation" "$variables"
}

# Cleanup review app services
cleanup_review_app() {
    local pr_pattern="pr-${PR_NUMBER}-"

    log_info "Cleaning up review app services for PR #${PR_NUMBER}"

    # If commit SHA is provided, clean up specific commit
    if [ -n "$COMMIT_SHA" ] && [ "$COMMIT_SHA" != "unknown" ]; then
        pr_pattern="pr-${PR_NUMBER}-${COMMIT_SHA}"
        log_info "Cleaning up specific commit: $COMMIT_SHA"
    else
        log_info "Cleaning up all services for PR #${PR_NUMBER}"
    fi

    # List all services
    local services_response
    services_response=$(list_services "$ZEABUR_PROJECT_ID")

    if echo "$services_response" | jq -e '.errors' > /dev/null; then
        log_error "Failed to list services:"
        echo "$services_response" | jq '.errors'
        exit 1
    fi

    # Find services matching the PR pattern
    local matching_services
    matching_services=$(echo "$services_response" | jq -r --arg pattern "$pr_pattern" '
        .data.services.edges[] |
        select(.node.name | contains($pattern)) |
        "\(.node._id) \(.node.name)"
    ')

    if [ -z "$matching_services" ]; then
        log_info "No services found matching pattern: $pr_pattern"
        return 0
    fi

    log_info "Found services to delete:"
    echo "$matching_services"

    # Delete each matching service
    while IFS= read -r service_line; do
        local service_id service_name
        service_id=$(echo "$service_line" | cut -d' ' -f1)
        service_name=$(echo "$service_line" | cut -d' ' -f2-)

        log_info "Deleting service: $service_name ($service_id)"

        local delete_response
        delete_response=$(delete_service "$service_id")

        if echo "$delete_response" | jq -e '.errors' > /dev/null; then
            log_error "Failed to delete service $service_name:"
            echo "$delete_response" | jq '.errors'
        else
            local delete_success
            delete_success=$(echo "$delete_response" | jq -r '.data.deleteService')
            if [ "$delete_success" = "true" ]; then
                log_success "Successfully deleted service: $service_name"
            else
                log_error "Failed to delete service: $service_name (returned false)"
            fi
        fi
    done <<< "$matching_services"

    log_success "Cleanup completed for PR #${PR_NUMBER}"
}

# Show status of review app services
show_status() {
    local pr_pattern="pr-${PR_NUMBER}-"

    log_info "Checking status for PR #${PR_NUMBER}"

    # List all services
    local services_response
    services_response=$(list_services "$ZEABUR_PROJECT_ID")

    if echo "$services_response" | jq -e '.errors' > /dev/null; then
        log_error "Failed to list services:"
        echo "$services_response" | jq '.errors'
        exit 1
    fi

    # Find services matching the PR
    local matching_services
    matching_services=$(echo "$services_response" | jq -r --arg pattern "$pr_pattern" '
        .data.services.edges[] |
        select(.node.name | contains($pattern)) |
        "\(.node.name)"
    ')

    if [ -z "$matching_services" ]; then
        log_info "No active review app services found for PR #${PR_NUMBER}"
        return 0
    fi

    log_success "Active review app services for PR #${PR_NUMBER}:"
    echo "$matching_services"

    # Try to determine possible URLs
    echo "$matching_services" | while IFS= read -r service_name; do
        if [[ "$service_name" =~ pr-${PR_NUMBER}-([a-f0-9]+)$ ]]; then
            local commit_hash="${BASH_REMATCH[1]}"
            local domain="${DOMAIN_PREFIX}-pr-${PR_NUMBER}-${commit_hash}"
            log_info "Possible URL: https://${domain}.zeabur.app"
        fi
    done
}

# Main function
main() {
    local action="$1"

    case "$action" in
        deploy)
            check_dependencies
            validate_env
            deploy_review_app
            ;;
        cleanup)
            check_dependencies
            validate_env
            cleanup_review_app
            ;;
        status)
            check_dependencies
            validate_env
            show_status
            ;;
        *)
            echo "Usage: $0 <action> [options]"
            echo ""
            echo "Actions:"
            echo "  deploy   - Deploy a new review app"
            echo "  cleanup  - Clean up review app services"
            echo "  status   - Show status of review app services"
            echo ""
            echo "Environment variables required:"
            echo "  ZEABUR_API_KEY     - Zeabur API token"
            echo "  ZEABUR_PROJECT_ID  - Target project ID"
            echo "  PR_NUMBER          - Pull request number"
            echo "  COMMIT_SHA         - Git commit hash (optional)"
            echo ""
            echo "Project configuration (optional):"
            echo "  PROJECT_NAME         - Project name for review apps (default: 'Review App')"
            echo "  IGNORED_SERVICES     - Comma-separated service names to exclude (default: '')"
            echo "  CLEANUP_SERVICES     - Comma-separated service names to cleanup after deploy (default: '')"
            echo "  UPDATE_IMAGE_SERVICES - Comma-separated service name patterns to update with commit tags (default: '')"
            echo "  DOMAIN_PREFIX        - Domain prefix for review apps (default: 'app')"
            echo "  IMAGE_TAG_PREFIX     - Image tag prefix (default: 'sha')"
            echo ""
            echo "Examples:"
            echo "  PR_NUMBER=123 COMMIT_SHA=abc12345 $0 deploy"
            echo "  PR_NUMBER=123 $0 cleanup"
            echo "  PR_NUMBER=123 $0 status"
            echo ""
            echo "For detailed configuration and project-independent usage:"
            echo "  See scripts/README.md"
            exit 1
            ;;
    esac
}

main "$@"
