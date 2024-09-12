import argparse
import json
import os
import logging

import requests


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def fetch_github_data(repo, endpoint, params={}):
    """ Fetch data from a GitHub repository endpoint. """
    data = []
    page = 1
    base_url = f'https://api.github.com/repos/{repo}/{endpoint}'
    while True:
        logging.info(f"Processing {endpoint}, page {page}...")
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
    parser.add_argument('--override', action='store_true', help='Override existing files and fetch data')
    args = parser.parse_args()

    # Define the repository
    repo = args.repo

    # Check if issues file exists
    if os.path.exists(args.issues_file) and not args.override:
        logging.info(f"Issues file '{args.issues_file}' already exists. Use --override to fetch new data.")
    else:
        # Fetch issue data
        logging.info("Fetching issues...")
        issues = fetch_github_data(repo, 'issues', {'state': 'all', 'labels': 'type: bug'})

        # Save issues to a JSON file
        with open(args.issues_file, 'w') as file:
            json.dump(issues, file)
        logging.info(f"Issues saved to '{args.issues_file}'.")

    # Check if releases file exists
    if os.path.exists(args.releases_file) and not args.override:
        logging.info(f"Releases file '{args.releases_file}' already exists. Use --override to fetch new data.")
    else:
        # Fetch release data
        logging.info("Fetching releases...")
        releases = fetch_github_data(repo, 'releases')

        # Save releases to a JSON file
        with open(args.releases_file, 'w') as file:
            json.dump(releases, file)
        logging.info(f"Releases saved to '{args.releases_file}'.")

if __name__ == "__main__":
    main()
