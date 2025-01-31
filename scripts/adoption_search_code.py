import requests
import argparse

def get_code_results(token):
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

    def search_code(query, page=1):
        url = f'https://api.github.com/search/code?q=\"{query}\"+extension:py&page={page}'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def extract_hash_from_url(url):
        parts = url.split('/blob/')
        if len(parts) > 1:
            return parts[1].split('/')[0]
        return None

    unique_results = set()
    repo_code_results = {}
    for search_string in search_strings:
        page = 1
        while True:
            data = search_code(search_string, page)
            items = data.get('items', [])
            if not items:
                break

            for item in items:
                repository_url = item.get('repository', {}).get('html_url', '')
                repository_name = repository_url.split('/')[-1]

                if repository_name in ignored_repositories:
                    continue

                result_key = extract_hash_from_url(item['html_url'])
                if result_key:
                    if result_key not in unique_results:
                        unique_results.add(result_key)
                        if repository_name not in repo_code_results:
                            repo_code_results[repository_name] = []
                        repo_code_results[repository_name].append({
                            'url': item['html_url'],
                            'path': item['path'],
                            'repository': repository_name,
                            'repository_url': repository_url
                        })

            page += 1
            if 'next' not in data.get('links', {}):
                break

    return repo_code_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get code results with specific changes from GitHub.')
    parser.add_argument('token', help='Your GitHub access token')

    args = parser.parse_args()

    repo_code_results = get_code_results(args.token)
    for repository, results in repo_code_results.items():
        print(f"Repository: {repository}")
        for result in results:
            print(f"  URL: {result['url']}")
            print(f"  Path: {result['path']}")
            print(f"  Repository URL: {result['repository_url']}")
            print()
        print(f"Total Results for {repository}: {len(results)}\n")

    total_results = sum(len(results) for results in repo_code_results.values())
    print(f"Total Results: {total_results}")
