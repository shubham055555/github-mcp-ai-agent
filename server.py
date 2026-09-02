import os
import requests

from dotenv import load_dotenv
from mcp.server import MCPServer


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

if not GITHUB_TOKEN:
    raise ValueError("GITHUB_TOKEN is not set in .env")


# ============================================================
# GITHUB CONFIG
# ============================================================

GITHUB_API = "https://api.github.com"

HEADERS = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json",
}


# ============================================================
# MCP SERVER
# ============================================================

mcp = MCPServer("GitHub MCP Server")


# ============================================================
# TOOL 1 — LIST REPOSITORIES
# ============================================================

@mcp.tool()
def list_repositories() -> list[dict]:
    """
    List all repositories accessible to the authenticated
    GitHub user.

    Pagination is automatically handled.
    """

    all_repositories = []
    page = 1

    while True:

        response = requests.get(
            f"{GITHUB_API}/user/repos",
            headers=HEADERS,
            params={
                "per_page": 100,
                "page": page,
            },
            timeout=10,
        )

        response.raise_for_status()

        repositories = response.json()

        if not repositories:
            break

        all_repositories.extend(repositories)

        page += 1

    return [
        {
            "name": repo["name"],
            "full_name": repo["full_name"],
            "private": repo["private"],
            "url": repo["html_url"],
        }
        for repo in all_repositories
    ]


# ============================================================
# TOOL 2 — LIST ISSUES
# ============================================================

@mcp.tool()
def list_issues(
    owner: str,
    repo: str,
    state: str = "open",
) -> list[dict]:
    """
    List issues from a GitHub repository.

    Args:
        owner:
            GitHub username or organization.

        repo:
            Repository name.

        state:
            open, closed, or all.
    """

    if state not in {"open", "closed", "all"}:
        raise ValueError(
            "state must be one of: open, closed, all"
        )

    all_issues = []
    page = 1

    while True:

        response = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo}/issues",
            headers=HEADERS,
            params={
                "state": state,
                "per_page": 100,
                "page": page,
            },
            timeout=10,
        )

        response.raise_for_status()

        issues = response.json()

        if not issues:
            break

        # GitHub's issues endpoint also returns
        # pull requests, so remove them.
        actual_issues = [
            issue
            for issue in issues
            if "pull_request" not in issue
        ]

        all_issues.extend(actual_issues)

        page += 1

    return [
        {
            "number": issue["number"],
            "title": issue["title"],
            "state": issue["state"],
            "url": issue["html_url"],
        }
        for issue in all_issues
    ]


# ============================================================
# TOOL 3 — GET ISSUE
# ============================================================

@mcp.tool()
def get_issue(
    owner: str,
    repo: str,
    issue_number: int,
) -> dict:
    """
    Get details of a specific GitHub issue.
    """

    response = requests.get(
        f"{GITHUB_API}/repos/{owner}/{repo}/issues/{issue_number}",
        headers=HEADERS,
        timeout=10,
    )

    response.raise_for_status()

    issue = response.json()

    return {
        "number": issue["number"],
        "title": issue["title"],
        "state": issue["state"],
        "body": issue["body"],
        "author": issue["user"]["login"],
        "url": issue["html_url"],
    }


# ============================================================
# TOOL 4 — SEARCH ISSUES
# ============================================================

@mcp.tool()
def search_issues(
    query: str,
    owner: str | None = None,
    repo: str | None = None,
    state: str = "open",
) -> list[dict]:
    """
    Search GitHub issues using keywords.

    Use this tool when the user asks to:
    - find issues
    - search bugs
    - find errors
    - find feature requests
    - search issues by keyword

    Args:
        query:
            Keyword or phrase to search for.

        owner:
            GitHub username or organization.

            For this project, the authenticated GitHub
            owner is shubham055555.

        repo:
            Repository name, for example QueryMind.

        state:
            open, closed, or all.
    """

    if not query.strip():
        raise ValueError(
            "query cannot be empty"
        )

    if state not in {"open", "closed", "all"}:
        raise ValueError(
            "state must be one of: open, closed, all"
        )

    # --------------------------------------------------------
    # BUILD SEARCH QUERY
    # --------------------------------------------------------

    search_query = query.strip()

    # Search only actual issues
    search_query += " is:issue"

    # Owner restriction
    if owner:
        search_query += f" user:{owner}"

    # Repository restriction
    if owner and repo:
        search_query += f" repo:{owner}/{repo}"

    # State restriction
    if state != "all":
        search_query += f" state:{state}"

    # --------------------------------------------------------
    # GITHUB SEARCH API
    # --------------------------------------------------------

    response = requests.get(
        f"{GITHUB_API}/search/issues",
        headers=HEADERS,
        params={
            "q": search_query,
            "per_page": 100,
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    # --------------------------------------------------------
    # FORMAT RESULTS
    # --------------------------------------------------------

    results = []

    for issue in data.get("items", []):

        repository_url = issue.get(
            "repository_url"
        )

        repository = None

        if repository_url:
            repository = repository_url.split("/")[-1]

        results.append(
            {
                "number": issue["number"],
                "title": issue["title"],
                "state": issue["state"],
                "repository": repository,
                "url": issue["html_url"],
            }
        )

    return results


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":
    mcp.run()