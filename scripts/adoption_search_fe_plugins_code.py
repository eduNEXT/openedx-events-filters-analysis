import requests
import argparse
import time

def get_code_results(token):
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Searched in package.json — confirms the package is an actual dependency
    pkg_search_strings = [
        'frontend-plugin-framework',
    ]

    # Searched across JS/TS source files
    src_search_strings = [
        'PluginSlot',
        'PLUGIN_OPERATIONS',
    ]

    src_extensions = ['js', 'jsx', 'ts', 'tsx']

    ignored_repositories = [
        'frontend-plugin-framework',
    ]

    def search_code(query, qualifier, page=1):
        url = f'https://api.github.com/search/code?q="{query}"+{qualifier}&page={page}'
        for attempt in range(5):
            response = requests.get(url, headers=headers)
            if response.status_code == 403:
                wait = int(response.headers.get('Retry-After', 60))
                time.sleep(wait)
                continue
            response.raise_for_status()
            time.sleep(6)  # stay within 10 requests/minute
            return response.json()
        response.raise_for_status()

    def extract_hash_from_url(url):
        parts = url.split('/blob/')
        if len(parts) > 1:
            return parts[1].split('/')[0]
        return None

    def record_item(item, unique_results, repo_code_results):
        repository_url = item.get('repository', {}).get('html_url', '')
        repository_name = repository_url.split('/')[-1]
        if repository_name in ignored_repositories:
            return
        result_key = extract_hash_from_url(item['html_url'])
        if result_key and result_key not in unique_results:
            unique_results.add(result_key)
            if repository_name not in repo_code_results:
                repo_code_results[repository_name] = []
            repo_code_results[repository_name].append({
                'url': item['html_url'],
                'path': item['path'],
                'repository': repository_name,
                'repository_url': repository_url,
            })

    unique_results = set()
    repo_code_results = {}

    # Phase 1: collect repos that declare frontend-plugin-framework in package.json.
    # This is the authoritative adoption signal and the allowlist for phase 2.
    for search_string in pkg_search_strings:
        page = 1
        while True:
            data = search_code(search_string, 'filename:package.json', page)
            items = data.get('items', [])
            if not items:
                break
            for item in items:
                record_item(item, unique_results, repo_code_results)
            page += 1
            if 'next' not in data.get('links', {}):
                break

    confirmed_repos = set(repo_code_results.keys())

    # Phase 2: find specific usage in JS/TS files, restricted to confirmed repos
    # to avoid false positives from unrelated projects that happen to use the
    # same generic symbol names.
    for search_string in src_search_strings:
        for ext in src_extensions:
            page = 1
            while True:
                data = search_code(search_string, f'extension:{ext}', page)
                items = data.get('items', [])
                if not items:
                    break
                for item in items:
                    repository_name = item.get('repository', {}).get('html_url', '').split('/')[-1]
                    if repository_name in confirmed_repos:
                        record_item(item, unique_results, repo_code_results)
                page += 1
                if 'next' not in data.get('links', {}):
                    break

    return repo_code_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get frontend plugin framework adoption from GitHub code search.')
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
