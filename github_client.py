import os

import requests
from dotenv import load_dotenv


# Load variables from .env
load_dotenv()


class GitHubClient:
    """Client for interacting with the GitHub REST API."""

    BASE_URL = "https://api.github.com"

    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")

        if not self.token:
            raise ValueError(
                "GITHUB_TOKEN is not set. Please check your .env file."
            )

        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    # --------------------------------------------------
    # GET AUTHENTICATED USER
    # --------------------------------------------------

    def get_authenticated_user(self):
        """Return information about the authenticated GitHub user."""

        response = requests.get(
            f"{self.BASE_URL}/user",
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    # --------------------------------------------------
    # LIST REPOSITORIES
    # --------------------------------------------------

    def list_repositories(self):
        """Return repositories accessible to the authenticated user."""

        response = requests.get(
            f"{self.BASE_URL}/user/repos",
            headers=self.headers,
            params={
                "per_page": 100,
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    # --------------------------------------------------
    # LIST ISSUES
    # --------------------------------------------------

    def list_issues(self, owner, repo, state="open"):
        """Return issues for a GitHub repository."""

        response = requests.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/issues",
            headers=self.headers,
            params={
                "state": state,
                "per_page": 100,
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    # --------------------------------------------------
    # GET SINGLE ISSUE
    # --------------------------------------------------

    def get_issue(self, owner, repo, issue_number):
        """Return details of a specific GitHub issue."""

        response = requests.get(
            f"{self.BASE_URL}/repos/{owner}/{repo}/issues/{issue_number}",
            headers=self.headers,
            timeout=10,
        )

        response.raise_for_status()

        return response.json()


# ======================================================
# TESTING
# ======================================================

if __name__ == "__main__":

    client = GitHubClient()

    # --------------------------------------------------
    # 1. Test authentication
    # --------------------------------------------------

    print("=" * 60)
    print("GITHUB MCP SERVER - API TEST")
    print("=" * 60)

    user = client.get_authenticated_user()

    print(f"\nAuthenticated as: {user['login']}")

    # --------------------------------------------------
    # 2. Get repositories
    # --------------------------------------------------

    repositories = client.list_repositories()

    print(f"Repositories returned: {len(repositories)}")

    print("\nRepositories:")

    for repo in repositories:
        print(f"- {repo['full_name']}")

    # --------------------------------------------------
    # 3. Get QueryMind issues
    # --------------------------------------------------

    owner = "shubham055555"
    repo = "QueryMind"

    print("\n" + "=" * 60)
    print(f"ISSUES FOR {owner}/{repo}")
    print("=" * 60)

    issues = client.list_issues(owner, repo)

    print(f"\nOpen issues: {len(issues)}")

    if issues:

        for issue in issues:
            print(
                f"- #{issue['number']}: "
                f"{issue['title']}"
            )

    else:
        print("No open issues found.")

    # --------------------------------------------------
    # 4. Test single issue
    # --------------------------------------------------

    if issues:

        issue_number = issues[0]["number"]

        print("\n" + "=" * 60)
        print(f"DETAILS OF ISSUE #{issue_number}")
        print("=" * 60)

        issue = client.get_issue(
            owner,
            repo,
            issue_number,
        )

        print(f"\nTitle: {issue['title']}")
        print(f"State: {issue['state']}")
        print(f"URL: {issue['html_url']}")