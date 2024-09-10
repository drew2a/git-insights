import argparse
import os
import logging
from collections import defaultdict
from datetime import datetime, timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from git import Repo
from matplotlib.ticker import MaxNLocator


# Function to read and parse the .mailmap file
def parse_mailmap(repo_path):
    mailmap = {}
    try:
        with open(repo_path + '/.mailmap', 'r') as file:
            for line in file:
                canonical_name = ''
                for part in [n for n in line.split('>') if n != '\n' and n]:
                    name, email = part.split('<')
                    name = name.strip()
                    if not canonical_name:
                        canonical_name = name
                    mailmap[email] = canonical_name
    except FileNotFoundError:
        logging.warning(".mailmap file not found, continuing without it")
    return mailmap


# Function to process contributors' continuous activity periods
def process_activity_periods(contributors, window, granularity=7):
    """
    Processes the activity periods of contributors based on commit dates with a specified granularity.

    This function groups the commit dates of each contributor into continuous
    activity periods. A continuous activity period is defined as a time
    range where the gap between any two consecutive commits does not exceed
    the specified 'window' duration.

    Args:
        contributors (dict): A dictionary where keys are contributor names and values are sets of commit dates.
        window (timedelta): The maximum allowed gap between consecutive commits to be considered part of the same activity period.
        granularity (int): The minimum number of days to consider for an activity period. If an activity period is shorter than this, it is extended to match the granularity.

    Returns:
        dict: A dictionary where keys are contributor names and values are lists of tuples. Each tuple represents an activity period (start_date, end_date).
      """

    activity_periods = defaultdict(list)
    for contributor, dates in contributors.items():
        sorted_dates = sorted(list(dates))
        start_date = sorted_dates[0]
        last_date = start_date

        for date in sorted_dates[1:]:
            if date - last_date > window:
                # Adjust the period length based on the granularity
                actual_length = (last_date - start_date).days + 1
                period_length = max(actual_length, granularity)
                adjusted_end_date = start_date + timedelta(days=period_length)
                activity_periods[contributor].append((start_date, adjusted_end_date, actual_length))

                start_date = date
            last_date = date

        actual_length = (last_date - start_date).days + 1
        period_length = max(actual_length, granularity)
        adjusted_end_date = start_date + timedelta(days=period_length)
        # Append the last period
        activity_periods[contributor].append((start_date, adjusted_end_date, actual_length))

    return activity_periods


# Function to count contributors and their activity dates with a minimum contribution filter
def count_contributors(repo_path, branch, mailmap, exclusions, delta, window, granularity):
    repo = Repo(repo_path)
    contributors = defaultdict(set)
    if delta:
        since = datetime.now() - delta
        commits = list(repo.iter_commits(branch, since=since.strftime('%Y-%m-%d')))
    else:
        commits = list(repo.iter_commits(branch))
    total_commits = len(commits)
    logging.info(f"Analyzing {total_commits} commits...")

    # Iterating over commits in the specified branch
    for i, commit in enumerate(commits, start=1):
        commit_date = commit.committed_datetime.date()
        contributor = commit.author.email
        # Using mailmap to resolve duplicate contributors
        contributor = mailmap.get(contributor, commit.author.name)

        # Check if the contributor is not in the exclusions list
        if not any(exclusion in contributor for exclusion in exclusions):
            contributors[contributor].add(commit_date)

        # Print progress every 10% of the total commits
        if i % (total_commits // 10) == 0 or i == total_commits:
            logging.info(f"Processed {i}/{total_commits} commits ({(i / total_commits) * 100:.1f}%)")

    return process_activity_periods(contributors, window, granularity)


# Function to plot the data
def plot_contributors(activity_periods, args, less_than_year=False):
    plt.figure(figsize=(15, 20))
    color_map = plt.colormaps.get_cmap('hsv')
    y_labels = []
    y_ticks = []

    min_date = min(period[0] for periods in activity_periods.values() for period in periods)
    max_date = max(period[1] for periods in activity_periods.values() for period in periods)

    # Drawing bars for activity periods
    for i, (contributor, periods) in enumerate(activity_periods.items()):
        print(f"Contributor: {contributor}")
        y_labels.append(contributor)
        y_ticks.append(i)
        for start_date, end_date, duration in periods:
            print(f"  Activity period: {start_date} to {end_date}. Duration: {duration}")
            plt.barh(i, (end_date - start_date).days, left=start_date, height=0.4, color=color_map(i), edgecolor='black')

        # Adding horizontal lines for better readability
        linewidth = 1.0 if i % 10 == 0 else 0.5
        plt.axhline(i, color='gray', linestyle='--', linewidth=linewidth)

    # Adding gray vertical lines at the start of each year and labeling them
    current_year = min_date.year
    year_positions = []
    while current_year <= max_date.year:
        year_start = datetime(current_year, 1, 1)
        plt.axvline(year_start, color='gray', linestyle='-', linewidth=0.8)
        year_positions.append(year_start)
        current_year += 1

    plt.yticks(y_ticks, y_labels)
    plt.xlabel('Date')
    plt.ylabel('Contributors')
    plt.title('Continuous Contribution Periods of Contributors')
    if less_than_year:
        # Setting less frequent date ticks on x-axis and adding year labels
        plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    else:
        plt.gca().xaxis.set_major_locator(mdates.YearLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        plt.xticks(year_positions,
                   [datetime(year, 1, 1).strftime('%Y') for year in range(min_date.year, max_date.year + 1)])
    plt.xticks(rotation=45)
    plt.ylim(-1, len(activity_periods))
    # Calculate the total duration and buffer
    total_duration = (max_date - min_date).days
    buffer_days = int(total_duration * 0.01)  # 1% of the total duration
    buffer = timedelta(days=buffer_days)
    plt.xlim(min_date - buffer, max_date + buffer)
    plt.tight_layout()
    plt.savefig(args.activity_plot_file)
    logging.info(f"Activity plot saved to: {os.path.abspath(args.activity_plot_file)}")


def aggregate_contributors_by_time(activity_periods):
    unique_dates = set()
    end_dates = set()
    for periods in activity_periods.values():
        for start_date, end_date, _ in periods:
            unique_dates.add(start_date)
            unique_dates.add(end_date)
            end_dates.add(end_date)

    sorted_dates = sorted(unique_dates)

    contributor_count_by_date = defaultdict(int)
    for date in sorted_dates:
        for periods in activity_periods.values():
            for start_date, end_date, _ in periods:
                if start_date <= date <= end_date:
                    contributor_count_by_date[date] += 1

        if date in end_dates:
            contributor_count_by_date[date] -= 1

    return sorted(contributor_count_by_date.items())


def plot_contributor_count_over_time(aggregated_data, args):
    """
    Plots the number of contributors over time using a bar chart.

    Args:
        aggregated_data: A list of tuples, where each tuple contains a date and the corresponding number of contributors on that date.
    """

    dates, counts = zip(*aggregated_data)  # Unzip the date and count tuples

    plt.figure(figsize=(20, 6))

    # Define a color map for different counts
    unique_counts = sorted(set(counts))
    color_map = plt.colormaps.get_cmap('tab20')
    count_to_color = {count: color_map(i) for i, count in enumerate(unique_counts)}

    for i in range(len(dates) - 1):
        start_date = dates[i]
        end_date = dates[i + 1]
        count = counts[i]
        width = (end_date - start_date).days
        plt.bar(start_date, count, width=width, align='edge', edgecolor='black', color=count_to_color[count])

    # Set x-axis major locator and formatter
    plt.gca().xaxis.set_major_locator(mdates.YearLocator())
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    plt.xticks(rotation=45)

    # Set y-axis to have a step size of 1
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))

    # Set axis labels and title
    plt.xlabel('Date')
    plt.ylabel('Number of Contributors')
    plt.title('Number of Contributors Over Time')
    plt.grid(True)

    # Calculate the total duration and buffer for x-axis
    min_date = min(dates)
    max_date = max(dates)
    total_duration = (max_date - min_date).days
    buffer_days = int(total_duration * 0.01)  # 1% of the total duration
    buffer = timedelta(days=buffer_days)
    plt.xlim(min_date - buffer, max_date + buffer)

    # Add buffer for y-axis
    max_count = max(counts)
    y_buffer = max_count * 0.01  # 1% of the maximum count
    plt.ylim(-y_buffer, max_count + y_buffer)

    plt.tight_layout()
    plt.savefig(args.contributor_count_plot_file)
    logging.info(f"Contributor count plot saved to: {os.path.abspath(args.contributor_count_plot_file)}")


def main():
    parser = argparse.ArgumentParser(description='Plot contributor activity over time.')
    parser.add_argument('--repo_path', type=str, default='.', help='Path to the repository')
    parser.add_argument('--branch', type=str, default='main', help='Branch to analyze')
    parser.add_argument('--exclusions', nargs='*', default=["dependabot", "snyk"], help='List of contributors to exclude')
    parser.add_argument('--delta_days', type=int, default=365 * 30, help='Number of days to look back for commits')
    parser.add_argument('--window_days', type=int, default=90, help='Window of days for activity period')
    parser.add_argument('--granularity_days', type=int, default=15, help='Granularity of activity period in days')
    parser.add_argument('--contribution_duration', type=int, default=1, help='Minimum contribution duration to consider')
    parser.add_argument('--less_than_year', action='store_true', help='Use less frequent date ticks on x-axis')
    parser.add_argument('--activity_plot_file', type=str, default='out/activity_plot.png', help='File name for the activity plot')
    parser.add_argument('--contributor_count_plot_file', type=str, default='out/contributor_count_plot.png', help='File name for the contributor count plot')

    args = parser.parse_args()

    # Define color codes
    RESET = "\033[0m"
    COLORS = {
        'DEBUG': "\033[94m",    # Blue
        'INFO': "\033[92m",     # Green
        'WARNING': "\033[93m",  # Yellow
        'ERROR': "\033[91m",    # Red
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
    logging.info("Starting contributor activity analysis")
    mailmap = parse_mailmap(args.repo_path)

    # Analyzing the repository for continuous contribution periods
    activity_periods = count_contributors(
        args.repo_path, args.branch, mailmap, args.exclusions,
        delta=timedelta(days=args.delta_days),
        window=timedelta(days=args.window_days),
        granularity=args.granularity_days
    )

    activity_periods = dict(
        (c, p) for c, p in activity_periods.items() if sum(d for sd, ed, d in p) >= args.contribution_duration
    )

    # Plotting the contribution activity on the graph
    plot_contributors(activity_periods, args, less_than_year=args.less_than_year)

    # Aggregate contributor data by time
    aggregated_data = aggregate_contributors_by_time(activity_periods)

    # Plotting the number of contributors over time
    plot_contributor_count_over_time(aggregated_data, args)


if __name__ == '__main__':
    main()
