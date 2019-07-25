from github import Github, InputGitTreeElement
import re
import datetime
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument("-r", "--release", action="store_true", help="Release only mode")
parser.add_argument("-c", "--commit", action="store_true", help="Commit only mode")
parser.add_argument("-a", "--all", action="store_true", help="New commit and new release")

args = parser.parse_args()

g = Github("#######")

repo = g.get_user().get_repo("release_sandbox")

print(f"Repository: {repo.name} \nOwner: {repo.owner}")

# Repository master sha/ref
master_ref = repo.get_git_ref('heads/master')
master_sha = master_ref.object.sha
base_tree = repo.get_git_tree(master_sha)

# Create fake commit - https://stackoverflow.com/questions/38594717/how-do-i-push-new-files-to-github?rq=1
if args.commit or args.all:
    commit_message = input("New commit message:\n")
    # Edit README
    with open('README.md', 'a') as o:
        o.write(f"\nNew test line written on: {datetime.datetime.now()}\n")

    element_list = list()
    for entry in ['README.md']:
        with open(entry, 'rb') as input_file:
            data = input_file.read()
            element = InputGitTreeElement(entry, '100644', 'blob', data.decode("utf-8"))
            element_list.append(element)

    tree = repo.create_git_tree(element_list, base_tree)
    parent = repo.get_git_commit(master_sha)
    commit = repo.create_git_commit(commit_message, tree, [parent])
    master_ref.edit(commit.sha)

commits = repo.get_commits(master_ref.object.sha)
print(f"Total number of commits: {commits.totalCount}")
last_commit = commits[0]

print(f"Last commit: {last_commit.sha}")

if args.release or args.all:
    # Check if a release is currently opened (draft status)
    last_release = repo.get_releases()[0]

    print(f"Last release: {last_release.title} / {last_release.tag_name}")

    release_message = input("New release title:\n")
    if last_release and last_release.draft:
        print(f"Opened release found: {last_release.tag}")
    elif last_release:
        last_tag = last_release.tag_name
        digit_r = r'\d+'
        minor_version = re.findall(digit_r, last_tag)[-1]
        minor_version_index = last_tag.rfind(minor_version)

        last_tag_updated = last_tag[:minor_version_index]+str(int(minor_version)+1)+last_tag[minor_version_index+1:]
        print(f"From {last_tag} to {last_tag_updated}")

        tag = repo.create_git_tag(last_tag_updated, f"Version {last_tag_updated}", last_commit.sha, "commit")
        print(tag)
        release = repo.create_git_release(tag.tag, release_message, "This is a second test release created from API")

