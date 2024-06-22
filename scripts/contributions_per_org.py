import requests
import argparse

# Global headers for authentication
headers = {}

# Function to fetch pull requests
def fetch_pull_requests(org_name, repo_name, end_cursor=None):
    query = f"""
    {{
      repository(owner: "{org_name}", name: "{repo_name}") {{
        pullRequests(first: 100{' ,after: "' + end_cursor + '"' if end_cursor else ''}) {{
          nodes {{
            title
            url
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
def fetch_user_organizations(user_login):
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
    global headers
    headers = {
        'Authorization': f'bearer {access_token}',
        'Content-Type': 'application/json'
    }

    user_contributions = {}
    end_cursor = None
    has_next_page = True

    while has_next_page:
        data = fetch_pull_requests(org_name, repo_name, end_cursor)
        pull_requests = data['data']['repository']['pullRequests']['nodes']
        page_info = data['data']['repository']['pullRequests']['pageInfo']
        end_cursor = page_info['endCursor']
        has_next_page = page_info['hasNextPage']

        for pr in pull_requests:
            author_login = pr['author']['login']
            pr_info = {
                'title': pr['title'],
                'url': pr['url']
            }

            if unique_users_only and author_login in user_contributions:
                user_contributions[author_login]['contributions'].append(pr_info)
                continue

            if author_login not in user_contributions:
                user_data = fetch_user_organizations(author_login)
                if user_data.get('errors'):
                    print(f"Error fetching organizations for user {author_login}: {user_data['errors']}")
                    continue
                user_orgs = [org['login'] for org in user_data['data']['user']['organizations']['nodes']]
                if not user_orgs:
                    user_orgs = ['None']
                user_contributions[author_login] = {
                    'organizations': user_orgs,
                    'contributions': [pr_info]
                }
            else:
                user_contributions[author_login]['contributions'].append(pr_info)

    # Organize contributions by organization
    org_contributions = {}
    for user, details in user_contributions.items():
        for org in details['organizations']:
            if org not in org_contributions:
                org_contributions[org] = {
                    'contributors': {},
                    'total_contributions': 0
                }
            if user not in org_contributions[org]['contributors']:
                org_contributions[org]['contributors'][user] = {
                    'contributions': [],
                    'count': 0
                }
            org_contributions[org]['contributors'][user]['contributions'].extend(details['contributions'])
            org_contributions[org]['contributors'][user]['count'] += len(details['contributions'])
            org_contributions[org]['total_contributions'] += len(details['contributions'])

    # Display the results
    for org, org_details in org_contributions.items():
        print(f"Organization: {org}, Total Contributions: {org_details['total_contributions']}")
        for user, contributions_details in org_details['contributors'].items():
            print(f"  User: {user}, Number of PRs: {contributions_details['count']}")
            for contribution in contributions_details['contributions']:
                print(f"    - {contribution['title']} ({contribution['url']})")
        print()

# Argument parser setup
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch pull requests from a GitHub repository and list unique users with their organizations and contributions.')
    parser.add_argument('access_token', type=str, help='GitHub personal access token')
    parser.add_argument('org_name', type=str, help='Name of the organization that owns the repository')
    parser.add_argument('repo_name', type=str, help='Name of the repository')
    parser.add_argument('--unique', dest='unique_users_only', action='store_true', help='Count only unique users')
    args = parser.parse_args()

    process_pull_requests(args.access_token, args.org_name, args.repo_name, args.unique_users_only)
