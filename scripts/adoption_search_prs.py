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

    repo_cache = {}

    def search_pull_requests(query, page=1):
        url = f'https://api.github.com/search/issues?q={query}&type=pr&page={page}'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_pull_request_files(pr_url):
        response = requests.get(pr_url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_repo_info(repo_api_url):
        if repo_api_url not in repo_cache:
            response = requests.get(repo_api_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            repo_cache[repo_api_url] = {
                'html_url': data.get('html_url', ''),
                'is_fork': data.get('fork', False),
            }
        return repo_cache[repo_api_url]

    seen_pr_urls = set()
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

                pr_url = item['html_url']
                if pr_url in seen_pr_urls:
                    continue

                repo_api_url = item.get('repository_url', '')
                repository_name = repo_api_url.split('/')[-1]
                if repository_name in ignored_repositories:
                    continue

                pr_files_url = item['pull_request']['url'] + '/files'
                pr_files = get_pull_request_files(pr_files_url)
                for pr_file in pr_files:
                    patch_content = pr_file.get('patch', '')
                    if any(s in patch_content for s in search_strings):
                        seen_pr_urls.add(pr_url)
                        repo_info = get_repo_info(repo_api_url)
                        unique_prs.append({
                            'url': pr_url,
                            'description': item.get('title', ''),
                            'repository': repository_name,
                            'repository_url': repo_info['html_url'],
                            'is_fork': repo_info['is_fork'],
                            'author': item['user']['login'],
                        })
                        break

            page += 1
            if 'next' not in data.get('links', {}):
                break

    return unique_prs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Get pull requests with specific changes from GitHub.')
    parser.add_argument('token', help='Your GitHub access token')
    parser.add_argument('--db', help='Path to SQLite database file')
    parser.add_argument('--notes', help='Optional label for this run')

    args = parser.parse_args()

    prs = get_pull_requests(args.token)
    for pr in prs:
        print("URL:", pr['url'])
        print("Description:", pr['description'])
        print()

    if args.db:
        import db as dbmod
        dbmod.init_db(args.db)
        run_id = dbmod.record_run(args.db, 'adoption_search_prs', 'backend', args.notes)
        dbmod.record_pr_results(args.db, run_id, [
            {
                'pr_url': pr['url'],
                'title': pr['description'],
                'repository': pr['repository'],
                'repository_url': pr['repository_url'],
                'is_fork': pr['is_fork'],
                'author': pr['author'],
                'organization': None,
            }
            for pr in prs
        ])
