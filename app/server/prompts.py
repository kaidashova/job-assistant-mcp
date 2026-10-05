from mcp.server.mcpserver import MCPServer


def register_prompts(mcp: MCPServer) -> None:
    @mcp.prompt()
    def find_best_jobs(keywords: str = "python, AI", top_n: int = 3) -> str:
        """Find fresh remote jobs and recommend the best fits."""
        return (
            f"Search remote jobs posted in the last 7 days for: {keywords}. "
            f"Then use match_job_to_profile on the top candidates and tell me the {top_n} that "
            "fit me best. For each give: title, company, link, score, why it fits, which skills "
            "I lack, and which of my projects to highlight. Offer to save them."
        )

    @mcp.prompt()
    def prepare_application(job_id: str) -> str:
        """Draft a tailored cover letter and talking points for a saved job."""
        return (
            f"Call get_job and match_job_to_profile for {job_id}. Write a concise cover letter "
            "(max 200 words) that leads with my most relevant project, plus 3 interview talking "
            "points covering my skill gaps honestly."
        )
