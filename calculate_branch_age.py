import argparse
import datetime
import subprocess


def run_git_command(command, repo_path):
    return subprocess.check_output(command, cwd=repo_path, shell=True).decode('utf-8').strip()


def main():
    parser = argparse.ArgumentParser(description='Calculate the age of release branches.')
    parser.add_argument('--repo_path', type=str, required=True, help='Path to the repository')
    args = parser.parse_args()

    # Fetch all branches
    run_git_command('git fetch --all', args.repo_path)

    # Get all release branches
    branches = run_git_command('git branch -r', args.repo_path).split('\n')
    release_branches = [branch for branch in branches if 'origin/release' in branch]

    info = {}
    for branch in release_branches:
        branch = branch.strip()

        # Find the oldest commit in the main branch that's not in the release branch
        oldest_commit = run_git_command(f'git log --pretty=format:"%h" {branch}..origin/main | tail -1', args.repo_path)

        # Find the fork commit
        fork_commit = run_git_command(f'git merge-base {oldest_commit} {branch}', args.repo_path)

        # Get the dates for the fork commit and the latest commit
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

        info[latest_commit_date] = s

    for d in sorted(info.keys(), reverse=True):
        print(info[d])

if __name__ == '__main__':
    main()
