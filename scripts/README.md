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
**Domain Pattern**: `disfactory-pr-{PR_NUMBER}-{COMMIT_SHA}.zeabur.app`

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
