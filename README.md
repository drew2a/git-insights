# git-insights

> **Disclaimer:** This repository was entirely created by AI using [aider.chat](https://aider.chat/). All visualization ideas belong to @drew2a, but the code and documentation were written by ChatGPT-4 and Claude-3.5-Sonnet.

A collection of scripts for analyzing and visualizing Git repositories. Explore commit history, contributor activity,
code changes, and more with easy-to-use tools designed to help you gain insights into your codebase.

## Table of Contents

- [Prerequisites](#prerequisites)
- [plot_number_of_contributors.py](#plot_number_of_contributorspy)
    - [Configurable Parameters](#configurable-parameters)
    - [Examples](#examples)
- [calculate_branch_age.py](#calculate_branch_agepy)
- [plot_open_issues.py](#plot_open_issuespy)
    - [Configurable Parameters](#configurable-parameters-1)
    - [Examples](#examples-1)
- [plot_open_issues.py](#plot_open_issuespy)
    - [Configurable Parameters](#configurable-parameters-2)
    - [Examples](#examples-2)

## Prerequisites

You can install the required Python packages using:

```bash
pip install -r requirements.txt
```

## plot_number_of_contributors.py

`plot_number_of_contributors.py` is a versatile script designed to analyze and visualize contributor activity within a
Git repository. By examining commit history, it identifies continuous contribution periods and aggregates contributor
data over time, providing insights into both individual and collective engagement patterns. The script offers
configurable parameters to tailor the analysis, such as specifying the branch, excluding certain contributors, and
defining the time window for activity periods. It generates visualizations that highlight both all contributors and
those with sustained activity, making it a valuable tool for understanding contributor dynamics in a project.

The original work for this script was done
here: [GitHub Issue Comment](https://github.com/drew2a/ivory-tower/issues/1#issuecomment-1884614714).

### Configurable Parameters

The script `plot_number_of_contributors.py` accepts the following configurable parameters:

- `--repo_path`: Path to the repository. Default is the current directory (`.`).
- `--branch`: Branch to analyze. Default is `main`.
- `--exclusions`: List of contributors to exclude. Default is `["dependabot", "snyk"]`.
- `--delta_days`: Number of days to look back for commits. Default is 30 years (`365 * 30` days).
- `--window_days`: The maximum allowed gap between consecutive commits to be considered as part of the same activity
  period. For example, a 7-day window means that if the gap between two commits is less than or equal to 7 days, they
  are considered part of a continuous contribution period. Default is 90 days.
- `--granularity_days`: The minimum length of time that a contribution period must be to be considered. For instance, a
  1-day granularity means that any period shorter than 1 day is extended to 1 day. Default is 15 days.
- `--contribution_duration`: The minimum total number of days a contributor must have contributed to be included in the
  analysis. For example, a filter of "at least two days in total" means that only contributors who have made commits on
  two or more separate days throughout the entire period are included. Default is 1 day.
- `--less_than_year`: Use less frequent date ticks on x-axis. This is a flag, so it has no default value.
- `--activity_plot_file`: File name for the activity plot. Default is `out/activity_plot.png`.
- `--contributor_count_plot_file`: File name for the contributor count plot. Default is
  `out/contributor_count_plot.png`.

### Examples

To generate the graphs, follow these steps:

```bash
git clone <repository-url>
```

Then, use the following commands:

#### All Contributors

This example visualizes all contributors over time with a window of 90 days, granularity of 15 days, and a minimum
contribution duration of 1 day. This setting captures all contributors who have made at least one commit within any
90-day period, providing a broad view of contributor activity.

```bash
python plot_number_of_contributors.py --repo_path /path/to/repo --branch main --window_days 90 --granularity_days 15 --contribution_duration 1 --activity_plot_file all_contributors.png
```

![all_contributors](https://github.com/user-attachments/assets/59c44c57-ea72-4974-881a-f6a720ed57ff)

#### Continuous Contributors

This example focuses on continuous contributors, using a window of 90 days, granularity of 1 day, and a minimum
contribution duration of 30 days. It highlights contributors who have been consistently active, making contributions
over a longer period, thus offering insights into sustained engagement.

```bash
python plot_number_of_contributors.py --repo_path /path/to/repo --branch main --window_days 90 --granularity_days 1 --contribution_duration 30 --contributor_count_plot_file continuous_contributors.png
```

![ccontributors2](https://github.com/user-attachments/assets/bb11ab72-791a-46f6-9058-bb526f95bad6)

## calculate_branch_age.py

`calculate_branch_age.py` is a script designed to calculate and visualize the age of branches in a Git
repository. It fetches all branches, determines the fork and latest commit dates for each branch, and calculates
the age in days. The script then generates a horizontal bar plot showing the age of each branch, with additional labels
for the start and end dates of each branch's age.

### Configurable Parameters

The script `calculate_branch_age.py` accepts the following configurable parameters:

- `--repo_path`: Path to the repository. This parameter is required.
- `--output_file`: File name for the branch age plot. Default is `out/branch_ages.png`.
- `--branch_regex`: Regex pattern to filter branches. Default is `.+`.
- `--min_age`: Minimum age of branches to include in days. Default is `0`.
- `--main_branch`: Name of the main branch to compare against. Default is `main`.

### Examples

To generate the branch age plot, follow these steps:

Clone the target repository:

```bash
git clone <repository-url>
```

Then, use the following command to plot all branches older than 100 days for https://github.com/arvidn/libtorrent

```bash
python calculate_branch_age.py --repo_path ../../arvidn/libtorrent --main_branch master --min_age 100
```

![libtorrent_branch_ages](https://github.com/user-attachments/assets/1774e42f-fe64-40c3-b755-ebc5eda36309)

## plot_open_issues.py

`plot_open_issues.py` is a script designed to fetch and visualize open issues from a GitHub repository over time. It
allows you to analyze the trend of open issues and visualize release periods with optional coloring and timestamp
display.

Due to the limitations of the public GitHub REST API, the number of requests is restricted. To avoid frequent requests
to GitHub, the script operates in two stages: first, it fetches all issues and releases and saves them to files; then,
it analyzes these files.

### Configurable Parameters

The script `plot_open_issues.py` accepts the following configurable parameters:

- `--repo`: GitHub repository in the format "owner/repo". Default is `Tribler/tribler`.
- `--issues_file`: File to save issues data. Default is `out/issues.json`.
- `--releases_file`: File to save releases data. Default is `out/releases.json`.
- `--state`: State of issues to fetch (e.g., open, closed, all). Default is `all`.
- `--labels`: Labels to filter issues by. Default is `type: bug`.
- `--override`: Override existing files and fetch new data. This is a flag, so it has no default value.
- `--output_plot`: Output file for the plot. Default is `out/open_issues_plot.png`.
- `--show_release_timestamps`: Display release timestamps on the plot. This is a flag, so it has no default value.
- `--color_releases`: Color the release periods on the plot. This is a flag, so it has no default value.

### Examples

To generate the plot, use the following command:

```bash
python plot_open_issues.py --repo Tribler/tribler --labels "type: bug" --output_plot out/open_issues_plot.png --show_release_timestamps --color_releases
```

This command will fetch issues and releases from the specified repository, save the data to JSON files, and generate a
plot of open bugs over time with colored release periods and timestamps.

![open_issues_plot](https://github.com/user-attachments/assets/a2af5be3-35c1-4572-88ec-cca4f016b9ea)
