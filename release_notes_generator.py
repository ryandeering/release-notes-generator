"""This module generates release notes for a specific branch and sends them to a Slack channel."""

import logging

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from config import AZDO_ORGANIZATION_URL, AZDO_ORGANIZATION_PROJECT, SLACK_CHANNEL, BRANCH_NAME
from credentials import AZDO_TOKEN, SLACK_TOKEN

logging.basicConfig(level=logging.INFO)

class ReleaseNotesGenerator:
    """A class to generate release notes and send them to a Slack channel."""
    def __init__(self, azdo_token: str, org_url: str, org_project: str, slack_token: str) -> None:
        self.azdo_token = azdo_token
        self.org_url = org_url
        self.org_project = org_project
        self.slack_token = slack_token

    def generate_release_notes(self, branch_name: str) -> str:
        """Generate the release notes for the latest release of the specified branch."""
        release = self._get_latest_release(branch_name)

        if release is None:
            return ""

        message = self._get_deployment_report_message(release)

        return message

    def send_slack_message(self, channel: str, message: str) -> None:
        """Send a message to a Slack channel."""

        # Create a client instance for the Slack API
        client = WebClient(token=self.slack_token)

        # Send a message to the specified channel
        try:
            response = client.chat_postMessage(
                channel=channel,
                text=message
            )
            logging.info("Message sent - %s", response['ts'])
        except SlackApiError as error:
            logging.error("Error sending message - %s", error)

    def _get_latest_release(self, branch_name: str):
        """Get the latest release for the specified branch."""
        credentials = BasicAuthentication('', self.azdo_token)
        connection = Connection(base_url=self.org_url, creds=credentials)
        release_client = connection.clients.get_release_client()

        # Get the latest release for the specified branch
        releases = release_client.get_releases(
            project=self.org_project,
            source_branch_filter=branch_name,
            top=1,
        )

        if not releases:
            logging.error("No releases found for this branch")
            return None

        # Get the release ID for the latest release
        release_id = releases.value[0].id

        # Get details for the latest release using the release ID
        release = release_client.get_release(
             project=self.org_project,
             release_id=release_id,
        )

        return release

    def _get_deployment_report_message(self, release) -> str:

        credentials = BasicAuthentication('', self.azdo_token)
        connection = Connection(base_url=self.org_url, creds=credentials)

        # Get clients to interact with the Build, and Work Item Tracking APIs
        build_client = connection.clients.get_build_client()
        work_item_client = connection.clients.get_work_item_tracking_client()

        # Check if there is a deployment artifact associated with the release
        deployment_artifact = release.artifacts[0] if release.artifacts else None

        if deployment_artifact:
            message = f"Deployment Report for {release.name}\n"

            # If there is a deployment artifact, get the work items associated with it
            build_run_id = deployment_artifact.definition_reference['version'].id
            work_item_refs = build_client.get_build_work_items_refs(
                project=self.org_project,
                build_id=build_run_id
            )

            # Extract the work item IDs from the references
            work_item_ids = [ref.id for ref in work_item_refs]

            # Get the details of the work items associated with the build
            work_items = work_item_client.get_work_items(ids=work_item_ids)

            # Add the list of work items to the deployment report message
            message += "\nList of work items associated with Build:\n"
            for work_item in work_items:
                work_item_type = work_item.fields['System.WorkItemType']
                emoji = '🐞' if work_item_type == 'Bug' else '⭐'
                message += f"{emoji} {work_item.id} - {work_item.fields['System.Title']}\n"

        else:
            logging.error("No deployment artifact found for this release")
            message = ""

        return message

if __name__ == '__main__':
    release_notes_generator = ReleaseNotesGenerator(
        AZDO_TOKEN,
        AZDO_ORGANIZATION_URL,
        AZDO_ORGANIZATION_PROJECT,
        SLACK_TOKEN
    )

    # Call get_release_notes() function to get release information
    release_notes = release_notes_generator.generate_release_notes(BRANCH_NAME)

    # Call send_slack_message() function to send the release information to a Slack channel
    if release_notes:
        release_notes_generator.send_slack_message(SLACK_CHANNEL, release_notes)
    