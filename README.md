# git-insights
A collection of scripts for analyzing and visualizing Git repositories. Explore commit history, contributor activity, code changes, and more with easy-to-use tools designed to help you gain insights into your codebase.

## Configurable Parameters for `plot_number_of_contributors.py`

The script `plot_number_of_contributors.py` accepts the following configurable parameters:

- `--repo_path`: Path to the repository. Default is the current directory (`.`).
- `--branch`: Branch to analyze. Default is `main`.
- `--exclusions`: List of contributors to exclude. Default is `["dependabot", "snyk"]`.
- `--delta_days`: Number of days to look back for commits. Default is 30 years (`365 * 30` days).
- `--window_days`: Window of days for activity period. Default is 90 days.
- `--granularity_days`: Granularity of activity period in days. Default is 15 days.
- `--contribution_duration`: Minimum contribution duration to consider. Default is 1 day.
- `--less_than_year`: Use less frequent date ticks on x-axis. This is a flag, so it has no default value.
- `--activity_plot_file`: File name for the activity plot. Default is `out/activity_plot.png`.
- `--contributor_count_plot_file`: File name for the contributor count plot. Default is `out/contributor_count_plot.png`.

## Parameters for `plot_contributor_count_over_time`

The `plot_contributor_count_over_time` function takes the following parameters:

- `aggregated_data`: A list of tuples, where each tuple contains a date and the corresponding number of contributors on that date. This data is used to plot the number of contributors over time.

- `args`: An object containing various arguments, including:
  - `contributor_count_plot_file`: The file name where the contributor count plot will be saved.

This function generates a bar chart that visualizes the number of contributors over time, using the provided data.
