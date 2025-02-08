import os
from dataclasses import dataclass

from azure.devops.connection import Connection
from azure.devops.v7_1.work_item_tracking import WorkItem as RESTWorkItem, WorkItemTrackingClient
from dotenv import load_dotenv
from msrest.authentication import BasicAuthentication


@dataclass
class WorkItem:
    id: int
    title: str
    assigned_to: str
    description: str

    @staticmethod
    def from_rest_object(rest_work_item: RESTWorkItem) -> "WorkItem":
        return WorkItem(
            id=rest_work_item.id,
            title=rest_work_item.fields.get("System.Title"),
            assigned_to=rest_work_item.fields.get("System.AssignedTo", {}).get("displayName", "Unassigned"),
            description=rest_work_item.fields.get("System.Description", "No description available"),
        )


class Mimir:
    def __init__(self): 
        if not os.getenv("AZURE_DEVOPS_PAT"):
            load_dotenv()
        self._pat = os.getenv("AZURE_DEVOPS_PAT")
        self._organization = os.getenv("AZURE_DEVOPS_ORGANIZATION")
        self._project = os.getenv("AZURE_DEVOPS_PROJECT")
        self.client = self._get_client()

    def _get_client(self) -> WorkItemTrackingClient:
        creds = BasicAuthentication("", self._pat)
        connection = Connection(base_url=f"https://dev.azure.com/{self._organization}", creds=creds)
        return connection.clients.get_work_item_tracking_client()

    def get_work_item(self, work_item_id: int) -> WorkItem:
        work_item = self.client.get_work_item(work_item_id)
        return WorkItem.from_rest_object(work_item)
