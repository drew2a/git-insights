import argparse
import datetime
import logging
import os
import subprocess

import matplotlib.dates as mdates
import matplotlib.pyplot as plt


def run_git_command(command, repo_path):
    logging.info(f"Executing command: {command} in {repo_path}")
    return subprocess.check_output(command, cwd=repo_path, shell=True).decode('utf-8').strip()


def main():
    # Define color codes
    RESET = "\033[0m"
    COLORS = {
        'DEBUG': "\033[94m",  # Blue
        'INFO': "\033[92m",  # Green
        'WARNING': "\033[93m",  # Yellow
        'ERROR': "\033[91m",  # Red
        'CRITICAL': "\033[95m"  # Magenta
    }

    class ColoredFormatter(logging.Formatter):
        def format(self, record):
            log_fmt = f"{COLORS.get(record.levelname, RESET)}%(asctime)s - %(levelname)s - %(message)s{RESET}"
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)

    # Set up logging with colors
    handler = logging.StreamHandler()
    handler.setFormatter(ColoredFormatter())
    logging.basicConfig(level=logging.INFO, handlers=[handler])
    logging.info("Starting branch age calculation")

    parser = argparse.ArgumentParser(description='Calculate the age of release branches.')
    parser.add_argument('--repo_path', type=str, required=True, help='Path to the repository')
    parser.add_argument('--output_file', type=str, default='out/branch_ages.png',
                        help='File name for the branch age plot')
    parser.add_argument('--branch_regex', type=str, default='.+', help='Regex pattern to filter branches')
    parser.add_argument('--include_zero_age', action='store_true', help='Include branches with age 0 days')
    args = parser.parse_args()

    # Fetch all branches
    logging.info("Fetching all branches")
    run_git_command('git fetch --all', args.repo_path)

    # Get all release branches
    logging.info("Getting all release branches")
    branches = run_git_command('git branch -r', args.repo_path).split('\n')
    if not branches:
        logging.error("No branches found. Exiting.")
        return

    import re
    branch_pattern = re.compile(args.branch_regex)
    release_branches = [branch.strip() for branch in branches if branch_pattern.match(branch.strip())]

    info = {}
    for branch in release_branches:
        branch = branch.strip()

        # Find the oldest commit in the main branch that's not in the release branch
        logging.info(f"Finding oldest commit in main branch not in {branch}")
        oldest_commit = run_git_command(f'git log --pretty=format:"%h" {branch}..origin/main | tail -1', args.repo_path)

        # Find the fork commit
        if oldest_commit:
            logging.info(f"Finding fork commit for branch {branch}")
            fork_commit = run_git_command(f'git merge-base {oldest_commit} {branch}', args.repo_path)
        else:
            logging.warning(f"No oldest commit found for branch {branch}. Skipping fork commit calculation.")
            continue

        # Get the dates for the fork commit and the latest commit
        logging.info(f"Getting dates for fork commit {fork_commit} and latest commit in {branch}")
        fork_commit_date = run_git_command(f'git show -s --format=%ci {fork_commit}', args.repo_path)
        latest_commit_date = run_git_command(f'git log -1 --format=%ci {branch}', args.repo_path)

        # Convert dates to datetime objects
        fork_commit_date = datetime.datetime.strptime(fork_commit_date, '%Y-%m-%d %H:%M:%S %z')
        latest_commit_date = datetime.datetime.strptime(latest_commit_date, '%Y-%m-%d %H:%M:%S %z')

        # Calculate the age of the branch in days
        age = latest_commit_date - fork_commit_date
        age_days = age.days
        s = f"Branch: {branch}\n" \
            f"\tLatest commit date: {latest_commit_date}\n" \
            f"\tFork date: {fork_commit_date}\n" \
            f"\tFork commit: {fork_commit}\n" \
            f"\tAge: {age_days} days"

        if age_days > 0 or args.include_zero_age:
            info[latest_commit_date] = s

    logging.info("Calculating branch ages")

    # Prepare data for plotting
    branch_names = []
    start_dates = []
    end_dates = []
    for d in sorted(info.keys(), reverse=True):
        print(info[d])
        branch_info = info[d].split('\n')
        branch_name = branch_info[0].split(': ')[1]
        latest_commit_date = datetime.datetime.strptime(branch_info[1].split(': ')[1], '%Y-%m-%d %H:%M:%S%z')
        fork_date = datetime.datetime.strptime(branch_info[2].split(': ')[1], '%Y-%m-%d %H:%M:%S%z')

        branch_names.append(branch_name)
        start_dates.append(fork_date)
        end_dates.append(latest_commit_date)

    if not start_dates:
        logging.error("No valid branch data found. Exiting.")
        return

    # Plotting
    plt.figure(figsize=(12, max(5, len(branch_names))))
    bar_widths = [(end - start).days for start, end in zip(start_dates, end_dates)]
    plt.barh(branch_names, bar_widths, left=start_dates, color='skyblue', edgecolor='black')

    # Add labels to the bars
    for i, (start, width) in enumerate(zip(start_dates, bar_widths)):
        plt.text(start + datetime.timedelta(days=width/2), i, f'{width}\ndays', va='center', ha='center', color='black')
    plt.xlabel('Date')
    plt.ylabel('Branches')
    plt.title('Branch Ages')
    # Add labels for the start and end of each branch age
    for i, (start, end) in enumerate(zip(start_dates, end_dates)):
        plt.text(start - datetime.timedelta(days=1), i, start.strftime('%Y-%m-%d'), va='center', ha='right', color='black', fontsize=8, rotation=90)
        plt.text(end + datetime.timedelta(days=1), i, end.strftime('%Y-%m-%d'), va='center', ha='left', color='black', fontsize=8, rotation=90)

    plt.xticks([])
    plt.tight_layout()

    # Add vertical gray lines for each month
    current_month = min(start_dates).replace(day=1)
    while current_month <= max(end_dates):
        plt.axvline(current_month, color='gray', linestyle='--', linewidth=0.5)
        next_month = current_month.month % 12 + 1
        next_year = current_month.year + (current_month.month // 12)
        current_month = current_month.replace(year=next_year, month=next_month)

    plt.savefig(args.output_file)
    logging.info(f"Branch age plot saved to: {os.path.abspath(args.output_file)}")


if __name__ == '__main__':
    main()
