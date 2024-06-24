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

# Main function to process pull requests
def process_pull_requests(access_token, org_name, repo_name):
    global headers
    headers = {
        'Authorization': f'bearer {access_token}',
        'Content-Type': 'application/json'
    }

    all_contributions = []
    end_cursor = None
    has_next_page = True

    while has_next_page:
        data = fetch_pull_requests(org_name, repo_name, end_cursor)
        pull_requests = data['data']['repository']['pullRequests']['nodes']
        page_info = data['data']['repository']['pullRequests']['pageInfo']
        end_cursor = page_info['endCursor']
        has_next_page = page_info['hasNextPage']

        for pr in pull_requests:
            pr_info = {
                'title': pr['title'],
                'url': pr['url'],
                'author': pr['author']['login']
            }
            all_contributions.append(pr_info)

    # Display all unique contributions
    print("All Unique Contributions:")
    for contribution in all_contributions:
        print(f"  URL: {contribution['url']}, Description: {contribution['title']}, Author: {contribution['author']}")

# Argument parser setup
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Fetch pull requests from a GitHub repository and list unique contributions.')
    parser.add_argument('access_token', type=str, help='GitHub personal access token')
    parser.add_argument('org_name', type=str, help='Name of the organization that owns the repository')
    parser.add_argument('repo_name', type=str, help='Name of the repository')
    args = parser.parse_args()

    process_pull_requests(args.access_token, args.org_name, args.repo_name)
