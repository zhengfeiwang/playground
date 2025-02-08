from mcp.server.fastmcp import FastMCP

from mimir import Mimir

mcp = FastMCP("Get Azure DevOps work item")


@mcp.tool()
def get_work_item(work_item_id: int) -> str:
    mimir = Mimir()
    work_item = mimir.get_work_item(work_item_id)
    return f"Work item {work_item.id} has title {work_item.title} and is assigned to {work_item.assigned_to}, description: {work_item.description}."


if __name__ == "__main__":
    mcp.run(transport="sse")
