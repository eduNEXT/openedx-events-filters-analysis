import requests
import argparse

# Function to fetch pull requests
def fetch_pull_requests(org_name, repo_name, headers, end_cursor=None):
    query = f"""
    {{
      repository(owner: "{org_name}", name: "{repo_name}") {{
        pullRequests(first: 100{' ,after: "' + end_cursor + '"' if end_cursor else ''}) {{
          nodes {{
            author {{
              login
            }}
          }}
          pageInfo {{
            endCursor
            hasNextPage
          }}
        }}
      }}
    }}
    """
    response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    return response.json()

# Function to fetch user organizations
def fetch_user_organizations(user_login, headers):
    query = f"""
    {{
      user(login: "{user_login}") {{
        organizations(first: 100) {{
          nodes {{
            login
          }}
        }}
      }}
    }}
    """
    response = requests.post('https://api.github.com/graphql', json={'query': query}, headers=headers)
    return response.json()

# Main function to process pull requests
def process_pull_requests(access_token, org_name, repo_name, unique_users_only):
    headers = {
        'Authorization': f'bearer {access_token}',
        'Content-Type': 'application/json'
    }

    unique_users = {}
    end_cursor = None
    has_next_page = True

    while has_next_page:
        data = fetch_pull_requests(org_name, repo_name, headers, end_cursor)
        pull_requests = data['data']['repository']['pullRequests']['nodes']
        page_info = data['data']['repository']['pullRequests']['pageInfo']
        end_cursor = page_info['endCursor']
        has_next_page = page_info['hasNextPage']

        for pr in pull_requests:
            author_login = pr['author']['login']

            if unique_users_only and author_login in unique_users:
                continue

            user_data = fetch_user_organizations(author_login, headers)
            if user_data.get('errors'):
                print(user_data.get('errors'))
                continue
            user_orgs = [org['login'] for org in user_data['data']['user']['organizations']['nodes']]
            unique_users[author_login] = user_orgs

    # Display the results
    for user, orgs in unique_users.items():
        print(f'User: {user}, Organizations: {", ".join(orgs) if orgs else "None"}')

    print(f'Total number of users who opened pull requests in the repository {repo_name} belonging to {org_name}: {len(unique_users)}')

# Argument parser setup
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch pull requests from a GitHub repository and list unique users with their organizations.')
    parser.add_argument('access_token', type=str, help='GitHub personal access token')
    parser.add_argument('org_name', type=str, help='Name of the organization that owns the repository')
    parser.add_argument('repo_name', type=str, help='Name of the repository')
    parser.add_argument('--unique', dest='unique_users_only', action='store_true', help='Count only unique users')
    args = parser.parse_args()

    process_pull_requests(args.access_token, args.org_name, args.repo_name, args.unique_users_only)
