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

    unique_prs = []
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
                        unique_prs.append({
                            'url': item['html_url'],
                            'description': item.get('title', '')
                        })
                        break

            page += 1
            if 'next' not in data.get('links', {}):
                break

    return unique_prs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get pull requests with specific changes from GitHub.')
    parser.add_argument('token', help='Your GitHub access token')

    args = parser.parse_args()

    prs = get_pull_requests(args.token)
    for pr in prs:
        print("URL:", pr['url'])
        print("Description:", pr['description'])
        print()
