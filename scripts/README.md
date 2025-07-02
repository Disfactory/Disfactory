# Zeabur Review App Scripts

This directory contains scripts for managing Zeabur review app deployments.

## Scripts Overview

### 🚀 Main Deployment Script
**`zeabur-review-app.sh`** - Comprehensive review app management
- **Actions**: `deploy`, `cleanup`, `status`
- **Features**: Commit-level isolation, automatic cleanup, health monitoring
- **Usage**: Called by GitHub Actions or manually for testing

### 🧪 Testing Scripts
**`test-zeabur-api.sh`** - Test deployment functionality
- Interactive project selection with `fzf`
- Template generation testing
- API connection verification
- Safe deployment testing

**`test-service-cleanup.sh`** - Test cleanup functionality
- Multi-select service deletion with `fzf`
- Confirmation prompts for safety
- Detailed cleanup reporting

## Quick Start

### Prerequisites
```bash
# Install required tools
brew install curl jq yq fzf  # macOS
# or
sudo apt install curl jq fzf && sudo snap install yq  # Ubuntu

# Install and configure Zeabur CLI
npm install -g @zeabur/cli
zeabur auth login
```

### Testing Deployment
```bash
# Test API connection and deployment
./scripts/test-zeabur-api.sh
```

### Testing Cleanup
```bash
# Test service cleanup (interactive)
./scripts/test-service-cleanup.sh
```

### Manual Deployment
```bash
# Set environment variables
export ZEABUR_API_KEY=$(yq '.token' ~/.config/zeabur/cli.yaml)
export ZEABUR_PROJECT_ID="your-project-id"
export PR_NUMBER="123"
export COMMIT_SHA="abc12345"

# Deploy review app
./scripts/zeabur-review-app.sh deploy

# Check status
./scripts/zeabur-review-app.sh status

# Cleanup when done
./scripts/zeabur-review-app.sh cleanup
```

## Project-Independent Usage

The `zeabur-review-app.sh` script is designed to be project-independent and can be used with any Zeabur project. It supports flexible configuration through environment variables or a configuration file.

### Quick Setup for Any Project

1. **Copy the script to your project:**
   ```bash
   cp scripts/zeabur-review-app.sh /path/to/your/project/scripts/
   ```

2. **Create a configuration file (optional):**
   ```bash
   # Create zeabur-config.env in your project root
   cat > zeabur-config.env << 'EOF'
   PROJECT_NAME="My Project"
   IGNORED_SERVICES="Worker,Background Service"
   CLEANUP_SERVICES="Database,Redis"
   UPDATE_IMAGE_SERVICES="Backend,API,Frontend"
   DOMAIN_PREFIX="myapp"
   IMAGE_TAG_PREFIX="sha"
   EOF
   ```

3. **Use with any project:**
   ```bash
   export ZEABUR_API_KEY="your-api-key"
   export ZEABUR_PROJECT_ID="your-project-id"
   export PR_NUMBER=123
   ./scripts/zeabur-review-app.sh deploy
   ```

### Configuration Examples

#### Web Application with Background Workers
```bash
PROJECT_NAME="My Web App"
IGNORED_SERVICES="Worker,Scheduler,Queue Processor"  # Exclude background services
UPDATE_IMAGE_SERVICES="Backend,Frontend"             # Update main app images
CLEANUP_SERVICES="PostgreSQL"                        # Remove duplicate database
DOMAIN_PREFIX="myapp"
```

#### Microservices Architecture
```bash
PROJECT_NAME="Microservices Stack"
IGNORED_SERVICES="Message Queue,Log Aggregator"      # Exclude infrastructure services
UPDATE_IMAGE_SERVICES="User Service,Order Service,Payment Service"  # Update business services
CLEANUP_SERVICES="Redis,MongoDB"                     # Clean up shared services
DOMAIN_PREFIX="microservices"
```

#### Simple API
```bash
PROJECT_NAME="Simple API"
IGNORED_SERVICES=""                                   # Include all services
UPDATE_IMAGE_SERVICES="API"                          # Update main service
CLEANUP_SERVICES=""                                   # No cleanup needed
DOMAIN_PREFIX="api"
```

### How It Works

1. **Template Processing**: Reads your `zeabur.yaml` template and creates a modified version for the review app
2. **Service Naming**: All services get suffixed with `-pr-{PR_NUMBER}-{COMMIT_SHA}`
3. **Service Filtering**: Services listed in `IGNORED_SERVICES` are excluded from review apps
4. **Image Updates**: Services matching patterns in `UPDATE_IMAGE_SERVICES` are updated with commit-specific tags
5. **Post-deployment Cleanup**: Services listed in `CLEANUP_SERVICES` are removed after deployment (useful for duplicate database services)
6. **Domain Generation**: Review app domains follow the pattern `{DOMAIN_PREFIX}-pr-{PR_NUMBER}-{COMMIT_SHA}.zeabur.app`

### Integration with CI/CD

#### GitHub Actions Example
```yaml
- name: Deploy Review App
  env:
    ZEABUR_API_KEY: ${{ secrets.ZEABUR_API_KEY }}
    ZEABUR_PROJECT_ID: ${{ secrets.ZEABUR_PROJECT_ID }}
    PR_NUMBER: ${{ github.event.pull_request.number }}
    COMMIT_SHA: ${{ github.sha }}
  run: |
    ./scripts/zeabur-review-app.sh deploy
```

#### GitLab CI Example
```yaml
deploy_review:
  script:
    - export PR_NUMBER=$CI_MERGE_REQUEST_IID
    - export COMMIT_SHA=$CI_COMMIT_SHORT_SHA
    - ./scripts/zeabur-review-app.sh deploy
  environment:
    name: review/$CI_MERGE_REQUEST_IID
    url: https://$DOMAIN_PREFIX-pr-$CI_MERGE_REQUEST_IID-$CI_COMMIT_SHORT_SHA.zeabur.app
```

## Script Details

### zeabur-review-app.sh

**Purpose**: Main script for all review app operations

**Actions**:
- `deploy` - Deploy a new review app with commit-specific naming
- `cleanup` - Remove all services for a PR (or specific commit)
- `status` - Show active review app services for a PR

**Features**:
- ✅ Dependency checking (curl, jq, yq)
- ✅ Environment validation
- ✅ Commit hash handling (auto-detection or manual)
- ✅ Service naming with PR and commit isolation
- ✅ GraphQL API integration
- ✅ Health monitoring and waiting
- ✅ GitHub Actions integration
- ✅ Colored output and detailed logging

**Service Naming**: `{ServiceName}-pr-{PR_NUMBER}-{COMMIT_SHA}`
**Domain Pattern**: `{DOMAIN_PREFIX}-pr-{PR_NUMBER}-{COMMIT_SHA}.zeabur.app` (configurable)

### test-zeabur-api.sh

**Purpose**: Interactive testing of deployment functionality

**Features**:
- ✅ API authentication testing
- ✅ Project selection with `fzf`
- ✅ Template generation and validation
- ✅ Optional test deployment
- ✅ Safe testing environment

**Usage Flow**:
1. Validates CLI configuration
2. Tests API connection
3. Lists available projects
4. Generates test template
5. Optionally deploys test instance

### test-service-cleanup.sh

**Purpose**: Interactive testing of cleanup functionality

**Features**:
- ✅ Service discovery and listing
- ✅ Multi-select deletion with `fzf`
- ✅ Confirmation prompts
- ✅ Detailed deletion reporting
- ✅ Error handling and recovery

**Usage Flow**:
1. Validates CLI configuration
2. Lists available projects
3. Shows services in selected project
4. Multi-select services for deletion
5. Confirms and executes cleanup

## Environment Variables

### Required for All Scripts
- `ZEABUR_API_KEY` - Your Zeabur API token
- `ZEABUR_PROJECT_ID` - Target Zeabur project ID

### Required for Main Script
- `PR_NUMBER` - Pull request number (or "main" for main branch)
- `COMMIT_SHA` - Git commit hash (optional, auto-detected if not provided)

### Project Configuration (Optional)
- `PROJECT_NAME` - Project name for review apps (default: "Review App")
- `IGNORED_SERVICES` - Comma-separated service names to exclude from review apps (default: "")
- `CLEANUP_SERVICES` - Comma-separated service names to cleanup after deployment (default: "")
- `UPDATE_IMAGE_SERVICES` - Comma-separated service name patterns to update with commit tags (default: "")
- `DOMAIN_PREFIX` - Domain prefix for review apps (default: "app")
- `IMAGE_TAG_PREFIX` - Image tag prefix (default: "sha")

### GitHub Actions Integration
- `GITHUB_ENV` - Set by GitHub Actions for exporting results

## Error Handling

All scripts include comprehensive error handling:

- **Dependency Checking**: Verifies required tools are installed
- **Authentication**: Tests API key validity before operations
- **Input Validation**: Validates environment variables and parameters
- **API Errors**: Handles and reports GraphQL API errors
- **Cleanup Safety**: Confirms destructive operations
- **Logging**: Detailed, colored output for troubleshooting

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   # Install missing tools
   brew install curl jq yq fzf  # macOS
   sudo apt install curl jq fzf && sudo snap install yq  # Ubuntu
   ```

2. **Authentication Errors**
   ```bash
   # Re-authenticate with Zeabur
   zeabur auth login

   # Verify token
   yq '.token' ~/.config/zeabur/cli.yaml
   ```

3. **Project ID Issues**
   ```bash
   # List your projects to find the correct ID
   ./scripts/test-zeabur-api.sh
   ```

4. **Template Generation Errors**
   ```bash
   # Verify zeabur.yaml is valid
   yq eval . zeabur.yaml
   ```

5. **Configuration Issues**
   ```bash
   # Check if configuration file is loaded
   ls -la zeabur-config.env

   # Test configuration variables
   source zeabur-config.env && echo "PROJECT_NAME: $PROJECT_NAME"
   ```

6. **Service Filtering Problems**
   ```bash
   # Test service filtering with dry run
   IGNORED_SERVICES="Service1,Service2" ./scripts/zeabur-review-app.sh deploy --dry-run
   ```

### Debug Mode

Run scripts with `set -x` for detailed execution:
```bash
bash -x ./scripts/zeabur-review-app.sh deploy
```

### API Testing

Test API connection manually:
```bash
export ZEABUR_API_KEY=$(yq '.token' ~/.config/zeabur/cli.yaml)

curl --request POST \
  --url https://api.zeabur.com/graphql \
  --header "Authorization: Bearer $ZEABUR_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{"query":"query { me { username } }"}'
```

## Integration with GitHub Actions

The main script is designed to work seamlessly with GitHub Actions:

```yaml
- name: Deploy review app
  env:
    ZEABUR_API_KEY: ${{ secrets.ZEABUR_API_KEY }}
    ZEABUR_PROJECT_ID: ${{ env.ZEABUR_PROJECT_ID }}
    PR_NUMBER: ${{ github.event.number }}
    COMMIT_SHA: ${{ github.event.pull_request.head.sha }}
  run: ./scripts/zeabur-review-app.sh deploy
```

Results are automatically exported to `$GITHUB_ENV` for use in subsequent steps.

## Security Notes

- Keep `ZEABUR_API_KEY` secure and rotate regularly
- Test scripts use safe, interactive operations
- Cleanup operations include confirmation prompts
- All API calls are logged for audit purposes

## Migration from Project-Specific Version

If you're migrating from a project-specific version of the tool:

1. **Create a configuration file** with your current hardcoded values:
   ```bash
   # Replace hardcoded values with configuration
   cat > zeabur-config.env << 'EOF'
   PROJECT_NAME="Your Current Project Name"
   IGNORED_SERVICES="Your Worker Service Name"
   UPDATE_IMAGE_SERVICES="Your Backend Service Pattern"
   DOMAIN_PREFIX="your-current-domain-prefix"
   EOF
   ```

2. **Update CI/CD scripts** to use the new configuration approach
3. **Test with a sample PR** to ensure everything works correctly

The tool is backward compatible - existing functionality will work with default values if no configuration is provided.

## Contributing

When modifying scripts:

1. **Test Thoroughly**: Use the test scripts to verify changes
2. **Maintain Compatibility**: Keep environment variable interfaces stable
3. **Add Error Handling**: Include proper error checking and user feedback
4. **Update Documentation**: Keep this README and the main docs updated
5. **Follow Conventions**: Use established naming patterns and logging format

## Support

For issues:
- Check script output and logs first
- Verify environment variables are set correctly
- Test API connection independently
- Review GitHub Actions logs for workflow issues
- Consult the main documentation at `docs/zeabur-review-app.md`
