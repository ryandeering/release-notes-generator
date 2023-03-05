"""
This module defines the configuration variables for release_notes_generator
.
Use this file to define the values for the following variables:
- AZDO_ORGANIZATION_URL: The URL of your Azure DevOps organization
- AZDO_ORGANIZATION_PROJECT: The name of your Azure DevOps project
- SLACK_CHANNEL: The name of the Slack channel to send the release notes to
- BRANCH_NAME: The name of the branch to generate release notes for
"""

AZDO_ORGANIZATION_URL = 'https://dev.azure.com/your-organization/'
AZDO_ORGANIZATION_PROJECT = 'your-project'
SLACK_CHANNEL = '#test-channel'
BRANCH_NAME = "refs/heads/main"
