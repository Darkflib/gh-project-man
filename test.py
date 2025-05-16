import os
import requests
from dotenv import load_dotenv
from rich import print

load_dotenv()
TOKEN = os.getenv("GITHUB_TOKEN")
if not TOKEN:
    raise ValueError("GITHUB_TOKEN is not set in the environment variables.")
# Sanity check for the token
if len(TOKEN) < 40:
    raise ValueError("GITHUB_TOKEN is too short. Please check your token.")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json"
}

def github_graphql_query(query: str, variables: dict = None):
    response = requests.post(
        'https://api.github.com/graphql',
        json={"query": query, "variables": variables or {}},
        headers=HEADERS
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        raise Exception(data["errors"])
    return data["data"]

def add_issue_to_project(project_id: str, issue_node_id: str):
    mutation = """
    mutation($projectId: ID!, $contentId: ID!) {
      addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
        item {
          id
        }
      }
    }
    """
    return github_graphql_query(mutation, {"projectId": project_id, "contentId": issue_node_id})

def set_project_field_value(project_id: str, item_id: str, field_id: str, value_id: str):
    mutation = """
    mutation($input: UpdateProjectV2ItemFieldValueInput!) {
      updateProjectV2ItemFieldValue(input: $input) {
        projectV2Item {
          id
        }
      }
    }
    """
    input_data = {
        "input": {
            "projectId": project_id,
            "itemId": item_id,
            "fieldId": field_id,
            "singleSelectOptionId": value_id
        }
    }
    return github_graphql_query(mutation, input_data)

def get_node_id_by_repository_issue(owner: str, repo: str, issue_number: int):
    query = """
    query($owner: String!, $repo: String!, $issueNumber: Int!) {
      repository(owner: $owner, name: $repo) {
        issue(number: $issueNumber) {
          id
        }
      }
    }
    """
    response = github_graphql_query(query, {"owner": owner, "repo": repo, "issueNumber": issue_number})
    return response["repository"]["issue"]["id"]

# Get the list of projects for a user
def get_user_projects(login: str):
    query = """
    query($login: String!) {
      user(login: $login) {
        projectsV2(first: 10) {
          nodes {
            id
            title
            number
            url
          }
        }
      }
    }
    """
    response = github_graphql_query(query, {"login": login})
    return response["user"]["projectsV2"]["nodes"]

def get_project_by_id(project_id: str):
    query = """
    query($projectId: ID!) {
      node(id: $projectId) {
        ... on ProjectV2 {
          id
          title
          url
        }
      }
    }
    """
    response = github_graphql_query(query, {"projectId": project_id})
    return response["node"]

def get_project_fields(project_id: str):
    # Get project fields
    query = """
    query($projectId: ID!) {
    node(id: $projectId) {
        ... on ProjectV2 {
        fields(first: 20) {
            nodes {
            id
            name
            dataType
            ... on ProjectV2SingleSelectField {
                options {
                id
                name
                }
            }
            }
        }
        }
    }
    }
    """
    response = github_graphql_query(query, {"projectId": project_id})
    return response["node"]["fields"]["nodes"]

def get_project_items(project_id: str):
    # Get project items
    query = """
    query($projectId: ID!) {
    node(id: $projectId) {
        ... on ProjectV2 {
        items(first: 20) {
            nodes {
            id
            title
            url
            ... on ProjectV2SingleSelectField {
                options {
                id
                name
                }
            }
            }
        }
        }
    }
    }
    """
    response = github_graphql_query(query, {"projectId": project_id})
    return response["node"]["items"]["nodes"]

def get_repositories_by_user(login: str):
    query = """
    query($login: String!) {
      user(login: $login) {
        repositories(first: 10) {
          nodes {
            id
            name
            url
          }
        }
      }
    }
    """
    response = github_graphql_query(query, {"login": login})
    return response["user"]["repositories"]["nodes"]

def get_repository_by_id(repo_id: str):
    query = """
    query($repoId: ID!) {
      node(id: $repoId) {
        ... on Repository {
          id
          name
          url
        }
      }
    }
    """
    response = github_graphql_query(query, {"repoId": repo_id})
    return response["node"]

def get_repository_issues(repo_id: str):
    query = """
    query($repoId: ID!) {
      node(id: $repoId) {
        ... on Repository {
          issues(first: 10) {
            nodes {
              id
              title
              url
            }
          }
        }
      }
    }
    """
    response = github_graphql_query(query, {"repoId": repo_id})
    return response["node"]["issues"]["nodes"]


