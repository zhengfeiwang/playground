from mcp.server.fastmcp import FastMCP

from mimir import Mimir
from raven import Raven

mcp = FastMCP("Get Azure DevOps work item")

raven = Raven()


@mcp.tool()
def get_work_item(work_item_id: int) -> str:
    work_item = raven.get_work_item(work_item_id)
    return str(work_item)


@mcp.tool()
def get_pull_request_reviews(pull_request_id: int) -> str:
    threads = raven.get_pull_request_threads(pull_request_id)
    return "\n\n".join(str(thread) for thread in threads)


@mcp.tool()
def plan(task: str) -> str:
    mimir = Mimir()
    return mimir.plan(task)


if __name__ == "__main__":
    mcp.run(transport="sse")
