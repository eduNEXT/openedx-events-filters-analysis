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
        '.send_event',
        'PipelineStep',
        'OpenEdxPublicFilter'
    ]

    ignored_repositories = [
        'openedx-events',
        'openedx-filters',
    ]

    def search_code(query, page=1):
        url = f'https://api.github.com/search/code?q={query}+extension:py&page={page}'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def extract_hash_from_url(url):
        parts = url.split('/blob/')
        if len(parts) > 1:
            return parts[1].split('/')[0]
        return None

    unique_results = set()
    all_code_results = []
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

                url_hash = extract_hash_from_url(item['html_url'])
                if url_hash:
                    result_key = (item['path'], repository_name, url_hash)
                    if result_key not in unique_results:
                        unique_results.add(result_key)
                        all_code_results.append({
                            'url': item['html_url'],
                            'path': item['path'],
                            'repository': repository_name,
                            'repository_url': repository_url
                        })

            page += 1
            if 'next' not in data.get('links', {}):
                break

    return all_code_results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get code results with specific changes from GitHub.')
    parser.add_argument('token', help='Your GitHub access token')

    args = parser.parse_args()

    all_code_results = get_code_results(args.token)
    for result in all_code_results:
        print(f"URL: {result['url']}, Path: {result['path']}, Repository: {result['repository']}, Repository URL: {result['repository_url']}")

    print(f"\nTotal Results: {len(all_code_results)}")
