# release-notes-generator

[![linting: pylint](https://img.shields.io/badge/linting-pylint-green)](https://github.com/ryandeering/release-notes-generator/actions)

This is a Python module that generates notes from the work items with the latest release in a specific branch in Azure DevOps and sends them to a Slack channel.

I wrote this code to be more 'Pythonic' than my previous last outing with Python, the Dublin Airport Security Bot. 

generate_release_notes generates the release notes for the latest release of the specified branch. The method uses the Azure DevOps Python SDK to query the latest release of the specified branch and retrieve the associated work items. If no releases are found for the specified branch, the method returns an empty string.

send_slack_message sends the release notes to a Slack channel using the Slack API. The method takes two arguments: the Slack channel name and the release notes message.

To use this module, you will need to provide the necessary credentials and configuration values in the config.py and credentials.py files.
