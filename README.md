# git-insights
A collection of scripts for analyzing and visualizing Git repositories. Explore commit history, contributor activity, code changes, and more with easy-to-use tools designed to help you gain insights into your codebase.

## Parameters for `plot_contributor_count_over_time`

The `plot_contributor_count_over_time` function takes the following parameters:

- `aggregated_data`: A list of tuples, where each tuple contains a date and the corresponding number of contributors on that date. This data is used to plot the number of contributors over time.

- `args`: An object containing various arguments, including:
  - `contributor_count_plot_file`: The file name where the contributor count plot will be saved.

This function generates a bar chart that visualizes the number of contributors over time, using the provided data.
