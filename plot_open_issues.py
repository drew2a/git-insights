import argparse
import json

import requests


def fetch_github_data(repo, endpoint, params={}):
    """ Fetch data from a GitHub repository endpoint. """
    data = []
    page = 1
    base_url = f'https://api.github.com/repos/{repo}/{endpoint}'
    while True:
        print(f"Processing {endpoint}, page {page}...")
        url = f'{base_url}?page={page}&per_page=100'
        response = requests.get(url, params=params)
        page_data = response.json()
        if page_data:
            data.extend(page_data)
            page += 1
        else:
            break
    return data


def main():
    parser = argparse.ArgumentParser(description='Fetch and save GitHub issues and releases.')
    parser.add_argument('--repo', type=str, default='Tribler/tribler', help='GitHub repository in the format "owner/repo"')
    parser.add_argument('--issues_file', type=str, default='out/issues.json', help='File to save issues data')
    parser.add_argument('--releases_file', type=str, default='out/releases.json', help='File to save releases data')
    args = parser.parse_args()

    # Define the repository
    repo = args.repo

    # Fetch issue data
    print("Fetching issues...")
    issues = fetch_github_data(repo, 'issues', {'state': 'all', 'labels': 'type: bug'})

    # Save issues to a JSON file
    with open(args.issues_file, 'w') as file:
        json.dump(issues, file)
    print(f"Issues saved to '{args.issues_file}'.")

    # Fetch release data
    print("Fetching releases...")
    releases = fetch_github_data(repo, 'releases')

    # Save releases to a JSON file
    with open(args.releases_file, 'w') as file:
        json.dump(releases, file)
    print(f"Releases saved to '{args.releases_file}'.")

if __name__ == "__main__":
    main()
