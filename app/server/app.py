from mcp.server.mcpserver import MCPServer

from app import __version__
from app.config import Settings
from app.constants.server import INSTRUCTIONS
from app.container import Services, build_services
from app.server.prompts import register_prompts
from app.server.resources import register_resources
from app.server.tools import register_tools


def build_server(services: Services | None = None) -> MCPServer:
    services = services or build_services()
    mcp = MCPServer("job-assistant", instructions=INSTRUCTIONS, version=__version__)
    register_tools(mcp, services)
    register_resources(mcp, services)
    register_prompts(mcp)
    return mcp


def main() -> None:
    settings = Settings()
    mcp = build_server(build_services(settings))
    if settings.transport == "stdio":
        mcp.run("stdio")
    else:
        mcp.run("streamable-http", host=settings.host, port=settings.port)
