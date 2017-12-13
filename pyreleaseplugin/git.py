from subprocess import Popen, PIPE, STDOUT


def get_current_branch():

    p = Popen("git rev-parse --abbrev-ref HEAD", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    branch = p.stdout.read().strip()
    return branch


def get_current_commit_sha():
    p = Popen("git rev-parse --short HEAD", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    sha = p.stdout.read().strip()
    return sha


def is_tree_clean():
    """
    Check if git working tree is clean.

    Returns:
        False if there are uncommited changes, True otherwise
    """
    return False if Popen(["git", "diff-files", "--quiet"]).wait() else True


def commit_changes(version, commit_message=None):
    """
    Commit current release changes.

    Args:
        version (str): The version specifier to include in the commit message
        commit_message (str): The commit message
    """
    if commit_message is None:
        commit_message = "Update version file and changlog for release {}".format(version)
    code = Popen(["git", "commit", "-a", "-m", commit_message]).wait()
    if code:
        raise RuntimeError("Error committing changes")


def tag(version):
    """
    Add a tag to the release.

    Args:
        version (str): The version specifier to include in the commit message
    """
    tag = 'v' + version
    code = Popen(["git", "tag", tag]).wait()
    if code:
        raise RuntimeError("Error tagging release")


def push_code(branch):
    """
    Push code changes to git branch `branch`.
    """
    code = Popen(["git", "push", "origin", branch]).wait()
    if code:
        raise RuntimeError("Error pushing changes to git")


def push_tags():
    """
    Push tags to git.
    """
    code = Popen(["git", "push", "--tags"]).wait()
    if code:
        raise RuntimeError("Error pushing tags to git")


def push(release_branch):
    """
    Push commits and tags to Github.
    """
    push_code(release_branch)
    push_tags()
