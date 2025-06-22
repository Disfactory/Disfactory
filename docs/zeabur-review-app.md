# Zeabur Review App Deployment

This document describes the enhanced automated deployment system for review apps using Zeabur's cloud platform with commit-level isolation and label-based triggers.

## Overview

The review app system automatically deploys isolated instances of the Disfactory application for pull requests that are labeled with `review-app`. Each commit within a labeled PR gets its own dedicated deployment, enabling developers and reviewers to test specific changes in a production-like environment.

## Features

### Core Features
- **Label-Based Activation**: Only deploys for PRs labeled with `review-app`
- **Commit-Level Isolation**: Each commit gets its own deployment with unique URLs
- **Automatic Cleanup**: All review app services are cleaned up when PR is closed
- **Service Isolation**: PostgreSQL and backend services get unique names per PR and commit
- **Health Monitoring**: Waits for deployments to be ready before reporting success

### Advanced Features
- **Comprehensive Shell Script**: Complex logic moved to `scripts/zeabur-review-app.sh`
- **Multiple Actions**: Deploy, cleanup, and status checking capabilities
- **Main Branch Previews**: Optional deployment for main branch commits with `[preview]` tag
- **Detailed PR Comments**: Rich comments with commit information and cleanup status

## Quick Start

### 1. Add the `review-app` Label
To enable review app deployment for a PR, add the `review-app` label to your pull request.

### 2. Push Commits
Each new commit will trigger a new deployment with its own unique URL:
- First commit: `https://disfactory-pr-123-abc12345.zeabur.app`
- Second commit: `https://disfactory-pr-123-def67890.zeabur.app`

### 3. Review and Test
Use the URLs provided in PR comments to test your changes.

### 4. Automatic Cleanup
When the PR is closed, all review app services are automatically cleaned up.

## Setup

### 1. Prerequisites

- Zeabur account with API access
- GitHub repository with appropriate permissions
- Zeabur project ID for deployment

### 2. GitHub Secrets and Variables

Add the following to your GitHub repository:

**Required Secret:**
- `ZEABUR_API_KEY` - Your Zeabur API token

**Required Secret or Variable:**
- `ZEABUR_PROJECT_ID` - Your Zeabur project ID (can be stored as either a secret or repository variable)

To get your API token:
```bash
# Install Zeabur CLI
npm install -g @zeabur/cli

# Login to Zeabur
zeabur auth login

# Get your API token
yq '.token' ~/.config/zeabur/cli.yaml
```

### 3. Configuration Options

The workflow supports two ways to store the project ID:

**Option 1: Repository Secret**
- Go to Settings → Secrets and variables → Actions
- Add `ZEABUR_PROJECT_ID` as a secret

**Option 2: Repository Variable**
- Go to Settings → Secrets and variables → Actions → Variables tab
- Add `ZEABUR_PROJECT_ID` as a variable

The workflow will check secrets first, then fall back to variables: `${{ secrets.ZEABUR_PROJECT_ID || vars.ZEABUR_PROJECT_ID }}`

## Architecture

### Service Naming Convention

For PR #123 with commit `abc12345`:
- `PostgreSQL` → `PostgreSQL-pr-123-abc12345`
- `Disfactory Backend` → `Disfactory Backend-pr-123-abc12345`

### Domain Generation

Each commit gets a unique domain:
- Pattern: `disfactory-pr-{PR_NUMBER}-{COMMIT_SHA}`
- Example: `https://disfactory-pr-123-abc12345.zeabur.app`

### Workflow Triggers

The GitHub Action responds to:
- **PR Events**: `opened`, `synchronize`, `reopened`, `closed`, `labeled`, `unlabeled`
- **Manual Dispatch**: Workflow can be triggered manually with custom parameters

## How It Works

### 1. Label Check
- Checks if PR has `review-app` label
- Only proceeds with deployment if label is present
- Cleanup happens when PR is closed (regardless of labels)

### 2. Deployment Process
1. **Template Generation**: Creates PR and commit-specific template
2. **Service Isolation**: Renames services with unique identifiers
3. **API Deployment**: Uses Zeabur GraphQL API to deploy services
4. **Health Check**: Waits for services to become accessible
5. **PR Comment**: Updates PR with deployment information

### 3. Cleanup Process
1. **Service Discovery**: Finds all services matching PR pattern
2. **Batch Deletion**: Removes all PR-related services
3. **Comment Update**: Marks cleanup as completed in PR

## Shell Script Usage

The `scripts/zeabur-review-app.sh` script can be used independently:

### Deploy a Review App
```bash
export ZEABUR_API_KEY="your-api-key"
export ZEABUR_PROJECT_ID="your-project-id"
export PR_NUMBER="123"
export COMMIT_SHA="abc12345"

./scripts/zeabur-review-app.sh deploy
```

### Cleanup Review App Services
```bash
export ZEABUR_API_KEY="your-api-key"
export ZEABUR_PROJECT_ID="your-project-id"
export PR_NUMBER="123"

# Clean up all commits for this PR
./scripts/zeabur-review-app.sh cleanup

# Clean up specific commit (set COMMIT_SHA)
export COMMIT_SHA="abc12345"
./scripts/zeabur-review-app.sh cleanup
```

### Check Review App Status
```bash
export ZEABUR_API_KEY="your-api-key"
export ZEABUR_PROJECT_ID="your-project-id"
export PR_NUMBER="123"

./scripts/zeabur-review-app.sh status
```

## Manual Workflow Dispatch

The workflow can be triggered manually from the GitHub Actions tab for advanced use cases:

### How to Use Manual Dispatch

1. Go to your repository on GitHub
2. Click on the "Actions" tab
3. Select "Deploy Zeabur Review App" workflow
4. Click "Run workflow" button
5. Fill in the required parameters:
   - **PR Number**: The pull request number (e.g., `123`)
   - **Commit SHA**: Optional commit hash (defaults to HEAD if not provided)
   - **Action**: Choose from `deploy`, `cleanup`, or `status`

### Use Cases

**Deploy Specific Commit**
- Useful for deploying a specific commit that wasn't auto-deployed
- Example: After image build completes, manually trigger deployment

**Cleanup Old Deployments**
- Clean up review app services without closing the PR
- Useful for cost management or troubleshooting

**Check Status**
- View all active review app services for a PR
- Useful for debugging and monitoring

### Example Scenarios

```yaml
# Deploy PR #123 with latest commit
PR Number: 123
Commit SHA: (leave empty)
Action: deploy

# Deploy specific commit
PR Number: 123  
Commit SHA: abc12345
Action: deploy

# Clean up all services for PR #123
PR Number: 123
Commit SHA: (leave empty)
Action: cleanup

# Check status of PR #123 services
PR Number: 123
Commit SHA: (leave empty)
Action: status
```

## Testing Scripts

### Test Deployment
Use the comprehensive test script:
```bash
./scripts/test-zeabur-api.sh
```

### Test Cleanup
Use the service cleanup test script:
```bash
./scripts/test-service-cleanup.sh
```

Both scripts include:
- Dependency checking
- API authentication verification
- Interactive project/service selection with `fzf`
- Real API testing capabilities

## Main Branch Previews

Enable main branch previews by including `[preview]` in commit messages:

```bash
git commit -m "feat: new feature [preview]"
git push origin main
```

This creates a preview deployment at:
- Pattern: `disfactory-pr-main-{COMMIT_SHA}.zeabur.app`
- Example: `https://disfactory-pr-main-abc12345.zeabur.app`

## Template Structure

The generated template includes commit-specific naming:

```yaml
apiVersion: zeabur.com/v1
kind: Template
metadata:
  name: "Disfactory PR #123 (abc12345)"
spec:
  description: "Review app for PR #123 at commit abc12345"
  variables:
    - key: BACKEND_DOMAIN
      type: DOMAIN
      name: Backend Domain
      description: Domain for the Disfactory backend API
  services:
    - name: PostgreSQL-pr-123-abc12345
      # ... PostgreSQL configuration
    - name: Disfactory Backend-pr-123-abc12345
      domainKey: BACKEND_DOMAIN
      dependencies:
        - PostgreSQL-pr-123-abc12345
      # ... backend configuration
```

## Troubleshooting

### Common Issues

1. **No Deployment Triggered**
   - Ensure PR has `review-app` label
   - Check GitHub Actions logs for label detection

2. **API Authentication Failed**
   - Verify `ZEABUR_API_KEY` secret is set correctly
   - Test locally: `yq '.token' ~/.config/zeabur/cli.yaml`

3. **Template Generation Errors**
   - Ensure `yq` is installed and working
   - Check `zeabur.yaml` is valid YAML

4. **Deployment Failures**
   - Check Zeabur dashboard for service status
   - Verify project ID and permissions

5. **Cleanup Issues**
   - Services may have dependencies preventing deletion
   - Check deletion order in script logs

### Debug Commands

```bash
# Test API connection
export ZEABUR_API_KEY="your-api-key"
curl --request POST \
  --url https://api.zeabur.com/graphql \
  --header "Authorization: Bearer $ZEABUR_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{"query":"query { me { username } }"}'

# List services for a project
./scripts/zeabur-review-app.sh status

# Test template generation
PR_NUMBER=999 COMMIT_SHA=testtest ./scripts/zeabur-review-app.sh deploy --dry-run
```

## Best Practices

### For Developers
1. **Use Labels Strategically**: Only add `review-app` label when you need live testing
2. **Test Incrementally**: Each commit gets its own URL, so test changes progressively
3. **Clean Communication**: Use descriptive commit messages for better tracking

### For Reviewers
1. **Check Latest Commit**: Always use the URL for the latest commit
2. **Test Thoroughly**: Each deployment is isolated, so test comprehensively
3. **Report Issues**: Use commit-specific URLs when reporting problems

### For Maintainers
1. **Monitor Costs**: Each commit creates new services, monitor Zeabur usage
2. **Label Management**: Consider automation for adding/removing `review-app` labels
3. **Cleanup Verification**: Periodically verify cleanup is working correctly

## Limitations

### Current Limitations
- **Resource Usage**: Each commit creates new services (may increase costs)
- **Startup Time**: Services take time to initialize (2-5 minutes typical)
- **Database Isolation**: Each commit gets its own database (data not shared)

### Planned Improvements
- [ ] Database sharing between commits of same PR
- [ ] Faster deployment through image caching
- [ ] Cost optimization for multiple commits
- [ ] Integration with PR status checks
- [ ] Deployment notifications in Slack/Discord

## API Reference

### GraphQL Mutations

#### Deploy Template
```graphql
mutation DeployTemplate($rawSpecYaml: String, $variables: Map, $projectID: ObjectID) {
  deployTemplate(rawSpecYaml: $rawSpecYaml, variables: $variables, projectID: $projectID) {
    _id
    name
    region { id }
  }
}
```

#### Delete Service
```graphql
mutation deleteService($id: ObjectID!) {
  deleteService(_id: $id)
}
```

### GraphQL Queries

#### List Services
```graphql
query Services($projectId: ObjectID) {
  services(projectID: $projectId) {
    edges {
      node {
        name
        _id
      }
    }
  }
}
```

## Support

### Getting Help
- **GitHub Actions Issues**: Check repository Actions tab
- **Zeabur API Issues**: Refer to [Zeabur documentation](https://zeabur.com/docs)
- **Script Issues**: Check script logs and validate environment variables

### Contributing
1. Test changes with the provided test scripts
2. Update documentation for new features
3. Follow the established naming conventions
4. Add appropriate error handling

### Security Notes
- Keep `ZEABUR_API_KEY` secure and rotate regularly
- Limit repository access to trusted contributors
- Monitor deployment logs for sensitive information leaks
