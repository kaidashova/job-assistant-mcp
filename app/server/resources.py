from mcp.server.mcpserver import MCPServer

from app.container import Services
from app.schemas import Profile


def register_resources(mcp: MCPServer, svc: Services) -> None:
    @mcp.resource("jobs://pipeline", mime_type="application/json")
    async def pipeline() -> str:
        """Application tracker snapshot."""
        return svc.tracker.pipeline().model_dump_json(indent=2)

    @mcp.resource("profile://me", mime_type="application/json")
    async def profile_resource() -> str:
        """The stored candidate profile."""
        return (svc.profile.get() or Profile()).model_dump_json(indent=2)
