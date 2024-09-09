# git-insights
A collection of scripts for analyzing and visualizing Git repositories. Explore commit history, contributor activity, code changes, and more with easy-to-use tools designed to help you gain insights into your codebase.

## Configurable Parameters for `plot_number_of_contributors.py`

The script `plot_number_of_contributors.py` accepts the following configurable parameters:

- `--repo_path`: Path to the repository. Default is the current directory (`.`).
- `--branch`: Branch to analyze. Default is `main`.
- `--exclusions`: List of contributors to exclude. Default is `["dependabot", "snyk"]`.
- `--delta_days`: Number of days to look back for commits. Default is 30 years (`365 * 30` days).
- `--window_days`: The maximum allowed gap between consecutive commits to be considered as part of the same activity period. For example, a 7-day window means that if the gap between two commits is less than or equal to 7 days, they are considered part of a continuous contribution period. Default is 90 days.
- `--granularity_days`: The minimum length of time that a contribution period must be to be considered. For instance, a 1-day granularity means that any period shorter than 1 day is extended to 1 day. Default is 15 days.
- `--contribution_duration`: The minimum total number of days a contributor must have contributed to be included in the analysis. For example, a filter of "at least two days in total" means that only contributors who have made commits on two or more separate days throughout the entire period are included. Default is 1 day.
- `--less_than_year`: Use less frequent date ticks on x-axis. This is a flag, so it has no default value.
- `--activity_plot_file`: File name for the activity plot. Default is `out/activity_plot.png`.
- `--contributor_count_plot_file`: File name for the contributor count plot. Default is `out/contributor_count_plot.png`.

## Examples

### All Contributors
This example visualizes all contributors over time with a window of 90 days, granularity of 15 days, and a minimum contribution duration of 1 day. This setting captures all contributors who have made at least one commit within any 90-day period, providing a broad view of contributor activity.

![all_contributors](https://github.com/user-attachments/assets/59c44c57-ea72-4974-881a-f6a720ed57ff)

### Continuous Contributors
This example focuses on continuous contributors, using a window of 90 days, granularity of 1 day, and a minimum contribution duration of 30 days. It highlights contributors who have been consistently active, making contributions over a longer period, thus offering insights into sustained engagement.

![ccontributors2](https://github.com/user-attachments/assets/bb11ab72-791a-46f6-9058-bb526f95bad6)

The `plot_contributor_count_over_time` function takes the following parameters:

- `aggregated_data`: A list of tuples, where each tuple contains a date and the corresponding number of contributors on that date. This data is used to plot the number of contributors over time.

- `args`: An object containing various arguments, including:
  - `contributor_count_plot_file`: The file name where the contributor count plot will be saved.

This function generates a bar chart that visualizes the number of contributors over time, using the provided data.
