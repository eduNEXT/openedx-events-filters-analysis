import requests
import argparse

def get_pull_requests(token):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    search_strings = [
        'openedx_events',
        'openedx_filters',
        'openedx-events',
        'openedx-filters',
        'OpenEdxPublicSignal',
        '.send_event',
        'PipelineStep',
        'OpenEdxPublicFilter'
    ]

    ignored_repositories = [
        'openedx-events',
        'openedx-filters',
    ]

    def search_pull_requests(query, page=1):
        url = f'https://api.github.com/search/issues?q={query}&type=pr&page={page}'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_pull_request_files(pr_url):
        response = requests.get(pr_url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_user_organizations(user_url):
        response = requests.get(user_url + "/orgs", headers=headers)
        response.raise_for_status()
        return [org['login'] for org in response.json()]

    org_prs = {}
    for search_string in search_strings:
        page = 1
        while True:
            data = search_pull_requests(search_string, page)
            items = data.get('items', [])
            if not items:
                break

            for item in items:
                if not item.get('pull_request'):
                    continue

                repository_url = item.get('repository_url', '')
                repository_name = repository_url.split('/')[-1]

                if repository_name in ignored_repositories:
                    continue

                pr_files_url = item['pull_request']['url'] + '/files'
                pr_files = get_pull_request_files(pr_files_url)
                for pr_file in pr_files:
                    patch_content = pr_file.get('patch', '')
                    if any(search_string in patch_content for search_string in search_strings):
                        author_url = item['user']['url']
                        orgs = get_user_organizations(author_url)

                        for org in orgs:
                            if org not in org_prs:
                                org_prs[org] = []

                            org_prs[org].append({
                                'url': item['html_url'],
                                'description': item.get('title', '')
                            })
                        break

            page += 1
            if 'next' not in data.get('links', {}):
                break

    return org_prs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get pull requests with specific changes from GitHub.')
    parser.add_argument('token', help='Your GitHub access token')

    args = parser.parse_args()

    org_prs = get_pull_requests(args.token)
    for org, prs in org_prs.items():
        print(f"Organization: {org}")
        for pr in prs:
            print(f"  URL: {pr['url']}, Description: {pr['description']}")
        print(f"Total PRs for {org}: {len(prs)}\n")

    print("Summary of total PRs per organization:")
    for org, prs in org_prs.items():
        print(f"{org}: {len(prs)} PRs")
