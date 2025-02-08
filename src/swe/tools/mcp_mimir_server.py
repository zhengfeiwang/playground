from mcp.server.fastmcp import FastMCP

from mimir import Mimir

mcp = FastMCP("Get Azure DevOps work item")


@mcp.tool()
def get_work_item(work_item_id: int) -> str:
    mimir = Mimir()
    work_item = mimir.get_work_item(work_item_id)
    return str(work_item)


if __name__ == "__main__":
    mcp.run(transport="sse")
