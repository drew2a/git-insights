import argparse
import json
import logging
import os
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import pandas as pd
import requests

# Define color codes
RESET = "\033[0m"
COLORS = {
    'DEBUG': "\033[94m",  # Blue
    'INFO': "\033[92m",  # Green
    'WARNING': "\033[93m",  # Yellow
    'ERROR': "\033[91m",  # Red
    'CRITICAL': "\033[95m",  # Magenta
}


class ColoredFormatter(logging.Formatter):
    def format(self, record):
        log_fmt = f"{COLORS.get(record.levelname, RESET)}%(asctime)s - %(levelname)s - %(message)s{RESET}"
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


# Set up logging with colored formatter
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logging.basicConfig(level=logging.INFO, handlers=[handler])


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
    parser.add_argument('--repo', type=str, default='Tribler/tribler',
                        help='GitHub repository in the format "owner/repo"')
    parser.add_argument('--issues_file', type=str, default='out/issues.json', help='File to save issues data')
    parser.add_argument('--releases_file', type=str, default='out/releases.json', help='File to save releases data')
    parser.add_argument('--override', action='store_true', help='Override existing files and fetch data')
    parser.add_argument('--input_issues', type=str, default='issues.json', help='Input file for issues data')
    parser.add_argument('--input_releases', type=str, default='releases.json', help='Input file for releases data')
    parser.add_argument('--output_plot', type=str, default='open_issues_plot.png', help='Output file for the plot')
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

    # Load issues and releases from JSON files
    with open(args.input_issues, 'r') as file:
        issues = json.load(file)

    with open(args.input_releases, 'r') as file:
        releases = json.load(file)

    # Processing issue data
    logging.info("Processing issue data...")
    issue_data = []
    for issue in issues:
        created_at = datetime.strptime(issue['created_at'], '%Y-%m-%dT%H:%M:%SZ')
        closed_at = datetime.strptime(issue['closed_at'], '%Y-%m-%dT%H:%M:%SZ') if issue['closed_at'] else None
        is_pull_request = 'pull_request' in issue
        issue_data.append({'created_at': created_at, 'closed_at': closed_at, 'is_pull_request': is_pull_request})

    df_issues = pd.DataFrame(issue_data)

    # Initialize counters
    first_date = df_issues['created_at'].min().date()
    last_date = datetime.now().date()
    current_date = first_date
    one_day = timedelta(days=1)

    # Counting open issues by date
    open_issues = []
    while current_date <= last_date:
        count_open_issues = ((df_issues['created_at'].dt.date <= current_date) &
                             ((df_issues['closed_at'].isnull()) | (df_issues['closed_at'].dt.date > current_date)) &
                             (~df_issues['is_pull_request'])).sum()
        open_issues.append({'date': current_date, 'open_issues': count_open_issues})
        current_date += one_day

    df_open_issues = pd.DataFrame(open_issues)

    # Grouping releases by major.minor version and getting the earliest release date
    grouped_releases = {}
    for release in releases:
        version_parts = release['tag_name'].split('.')
        major_minor = '.'.join(version_parts[:2])
        release_date = datetime.strptime(release['published_at'], '%Y-%m-%dT%H:%M:%SZ').date()
        if major_minor in grouped_releases:
            grouped_releases[major_minor] = min(grouped_releases[major_minor], release_date)
        else:
            grouped_releases[major_minor] = release_date

    # Sorting releases by date
    sorted_releases = sorted(grouped_releases.items(), key=lambda x: x[1])

    # Rainbow colors
    colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

    # Plotting
    logging.info("Plotting Open Issues Over Time with Release Groups...")
    plt.figure(figsize=(18, 6))

    plt.plot(df_open_issues['date'], df_open_issues['open_issues'], marker='o', linestyle='-', label='Open Issues',
             markersize=4)

    # Adding colored rectangles for release groups
    for i, (version, start_date) in enumerate(sorted_releases):
        color = colors[i % len(colors)]
        end_date = sorted_releases[i + 1][1] if i + 1 < len(sorted_releases) else last_date
        plt.axvspan(start_date, end_date, color=color, alpha=0.3)
        plt.text(start_date, df_open_issues['open_issues'].max(), version, fontsize=8, color=color, ha='left')

    plt.title('Open Issues Over Time with Colored Release Periods')
    plt.xlabel('Date')
    plt.ylabel('Number of Open Issues')
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(args.output_plot)
    logging.info(f"Plot saved to '{args.output_plot}'.")

    logging.info("Visualization completed.")


if __name__ == "__main__":
    main()
