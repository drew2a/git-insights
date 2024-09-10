import datetime
import subprocess


def run_git_command(command, repo_path):
    return subprocess.check_output(command, cwd=repo_path, shell=True).decode('utf-8').strip()


# Repository path
repo_path = 'path/to/tribler/repo'

# Fetch all branches
run_git_command('git fetch --all', repo_path)

# Get all release branches
branches = run_git_command('git branch -r', repo_path).split('\n')
release_branches = [branch for branch in branches if 'origin/release' in branch]

info = {}
for branch in release_branches:
    branch = branch.strip()

    # Find the oldest commit in the main branch that's not in the release branch
    oldest_commit = run_git_command(f'git log --pretty=format:"%h" {branch}..origin/main | tail -1', repo_path)

    # Find the fork commit
    fork_commit = run_git_command(f'git merge-base {oldest_commit} {branch}', repo_path)

    # Get the dates for the fork commit and the latest commit
    fork_commit_date = run_git_command(f'git show -s --format=%ci {fork_commit}', repo_path)
    latest_commit_date = run_git_command(f'git log -1 --format=%ci {branch}', repo_path)

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

    info[latest_commit_date] = s

for d in sorted(info.keys(), reverse=True):
    print(info[d])
