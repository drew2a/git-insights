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


# Define the repository
repo = 'Tribler/tribler'

# Fetch issue data
print("Fetching issues...")
issues = fetch_github_data(repo, 'issues', {'state': 'all', 'labels': 'type: bug'})

# Save issues to a JSON file
with open('issues.json', 'w') as file:
    json.dump(issues, file)
print("Issues saved to 'issues.json'.")

# Fetch release data
print("Fetching releases...")
releases = fetch_github_data(repo, 'releases')

# Save releases to a JSON file
with open('releases.json', 'w') as file:
    json.dump(releases, file)
print("Releases saved to 'releases.json'.")