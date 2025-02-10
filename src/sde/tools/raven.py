import os
import typing
from dataclasses import dataclass

from azure.devops.connection import Connection
from azure.devops.v7_1.git import (
    Comment,
    CommentThreadContext,
    GitClient,
    GitPullRequestCommentThread,
)
from azure.devops.v7_1.work_item_tracking import WorkItem as RESTWorkItem, WorkItemTrackingClient
from dotenv import load_dotenv
from msrest.authentication import BasicAuthentication



@dataclass
class WorkItem:
    id: int
    type: str
    title: str
    assigned_to: str
    description: str

    @staticmethod
    def from_rest_object(rest_work_item: RESTWorkItem) -> "WorkItem":
        return WorkItem(
            id=rest_work_item.id,
            type=rest_work_item.fields.get("System.WorkItemType"),
            title=rest_work_item.fields.get("System.Title"),
            assigned_to=rest_work_item.fields.get("System.AssignedTo", {}).get("displayName", "Unassigned"),
            description=rest_work_item.fields.get("System.Description", "No description available"),
        )

    def __str__(self) -> str:
        return (
            f"Work item #{self.id}\n"
            f"Type: {self.type}\n"
            f"Title: {self.title}\n"
            f"Assigned to: {self.assigned_to}\n"
            f"Description:\n{self.description}\n"
        )


@dataclass
class PullRequestThread:
    file_path: str
    comments: typing.List[str]
    left_file: typing.Optional[str] = None
    right_file: typing.Optional[str] = None

    @staticmethod
    def from_rest_object(thread: GitPullRequestCommentThread) -> typing.Optional["PullRequestThread"]:
        thread_context: CommentThreadContext = thread.thread_context
        if thread_context is None:
            return None
        file_path = thread_context.file_path
        if thread_context.left_file_start is None or thread_context.left_file_end is None:
            left_file = None
        else:
            start, end = thread_context.left_file_start, thread_context.left_file_end
            left_file = f"L{start.line}:{start.offset}-L{end.line}:{end.offset}"
        if thread_context.right_file_start is None or thread_context.right_file_end is None:
            right_file = None
        else:
            start, end = thread_context.right_file_start, thread_context.right_file_end
            right_file = f"L{start.line}:{start.offset}-L{end.line}:{end.offset}"
        rest_comments: typing.List[Comment] = thread.comments
        comments = []
        for rest_comment in rest_comments:
            if rest_comment.comment_type == "system":
                continue
            comments.append(f"{rest_comment.author.display_name}: {rest_comment.content}")
        # we only care about comments from human reviewers, so if all comments are system comments, return None
        return PullRequestThread(file_path, comments, left_file, right_file) if len(comments) > 0 else None

    def __str__(self) -> str:
        metadata = (
            f"File: {self.file_path}\n"
            f"Left file: {self.left_file}\n"
            f"Right file: {self.right_file}"
        )
        comments = "\n - ".join(self.comments)
        return f"{metadata}\nComments:\n - {comments}"


class Raven:
    def __init__(self): 
        if not os.getenv("AZURE_DEVOPS_PAT"):
            load_dotenv()
        self._pat = os.getenv("AZURE_DEVOPS_PAT")
        self._organization = os.getenv("AZURE_DEVOPS_ORGANIZATION")
        self._project = os.getenv("AZURE_DEVOPS_PROJECT")
        self._repository_id = os.getenv("AZURE_DEVOPS_REPOSITORY_ID")
        creds = BasicAuthentication("", self._pat)
        self._connection = Connection(base_url=f"https://dev.azure.com/{self._organization}", creds=creds)
        self.work_item_client: WorkItemTrackingClient = self._connection.clients.get_work_item_tracking_client()
        self.git_client: GitClient = self._connection.clients.get_git_client()

    def get_pull_request_threads(self, pull_request_id: int) -> typing.List[PullRequestThread]:
        rest_threads: typing.List[GitPullRequestCommentThread] = self.git_client.get_threads(
            repository_id=self._repository_id,
            pull_request_id=pull_request_id,
            project=self._project,
        )
        threads = []
        for rest_thread in rest_threads:
            thread = PullRequestThread.from_rest_object(rest_thread)
            if thread is not None:
                threads.append(thread)
        return threads

    def get_work_item(self, work_item_id: int) -> WorkItem:
        work_item = self.work_item_client.get_work_item(work_item_id)
        return WorkItem.from_rest_object(work_item)
