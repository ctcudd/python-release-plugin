"""
This module defines a setuptools command that enables the following:

1. updating the version specifier in a version file
2. adding an entry to a changelog
3. committing the previous changes to Github
4. adding a Git tag to the release commit
5. publishing to a specified PyPi repository

python setup.py release --version 2.7.1

By default, the command will bump the patch version of the module if no version number is
specified.
"""

from datetime import datetime
import os
import re
from setuptools import Command
from subprocess import Popen

from pyreleaseplugin.clean import CleanCommand
from pyreleaseplugin.config import ReleaseConfig
from pyreleaseplugin.git import commit_changes, is_tree_clean, push, tag


VERSION_RE = re.compile('^__version__\s*=\s*"(.*?)"$', re.MULTILINE)


def current_version_from_version_file(version_file):
    with open(version_file, "r") as infile:
        contents = infile.read()

    m = VERSION_RE.search(contents)
    try:
        version = m.group(1)
    except:
        raise IOError(
            "Unable to find __version__ variable defined in {}".format(version_file))

    return version


def update_version_file(filename, new_version):
    """
    Update the version file at the path specified by `filename`.

    Args:
        filename (str): The path to the version file
        new_version (str): The new version specifier

    Returns:
        The new version specifier
    """
    old_version = current_version_from_version_file(filename)
    new_version = new_version or bump_patch_version(old_version)

    with open(filename, "r") as infile:
        contents = infile.read()

    contents = VERSION_RE.sub('__version__ = "{}"'.format(new_version), contents)

    with open(filename, "w") as outfile:
        outfile.write(contents)

    return new_version


def bump_patch_version(version):
    """
    Increment the patch version.

    Args:
        version (str): The version to bump
    """
    parts = [int(x) for x in version.split('.')]
    parts[2] += 1

    return '.'.join([str(x) for x in parts])


RELEASE_LINE_RE = re.compile("^([^\s]+) \(([^\)]+)\)$")


def add_changelog_entry(filename, new_version, message):
    """
    Add a new entry to the changelog specified by `filename`.

    Args:
        filename (str): The path to the changelog file
        new_version (str): The new version specifier
    """
    def head_and_tail(lines):
        head = []
        tail = [line for line in lines]

        while tail:
            if RELEASE_LINE_RE.search(tail[0]):
                break
            else:
                head.append(tail.pop(0))

        return (head, tail)

    with open(filename, "r") as infile:
        lines = [line.strip() for line in infile.readlines()]

    head, tail = head_and_tail(lines)
    date = datetime.now().strftime("%Y-%m-%d")
    new_entry_header = "{} ({})".format(new_version, date)
    new_entry = '\n'.join([new_entry_header, "-" * len(new_entry_header), message.strip()]) + '\n'

    new_head = '\n'.join(head).strip() + '\n'
    new_tail = '\n'.join(tail)
    new_text = '\n'.join([new_head, new_entry, new_tail])

    with open(filename, "w") as outfile:
        outfile.write(new_text.strip())


def get_input():
    """
    Get input from user until EOF is encountered.

    Returns:
        Each line entered joined by a newline
    """
    lines = []

    try:
        while True:
            lines.append(input())
    except EOFError:
        pass

    return '\n'.join(lines)


def parse_y_n_response(response):
    return True if response.strip().lower() in ('y', 'yes') else False


def build():
    """
    Build a wheel distribution.
    """
    code = Popen(["python", "setup.py", "clean", "bdist_wheel"]).wait()
    if code:
        raise RuntimeError("Error building wheel")


def publish_to_pypi():
    """
    Publish the distribution to our local PyPi.
    """
    code = Popen(["twine", "upload", "dist/*"]).wait()
    if code:
        raise RuntimeError("Error publishing to PyPi")


def get_description():
    """
    Prompt the user for a textual description of the work done in the release.

    Returns:
        Each line of the text inputted by the user joined by newlines
    """
    print("Enter a short description of the changes included in the release "
          "to include in the changelog, and enter CTRL-D to finish")
    return get_input().strip() + "\n\n"


class ReleaseCommand(Command):
    """
    A custom setuptools command for releasing a Python module.
    """
    description = "Update the module version, update the CHANGELOG, tag the commit, push the " \
                  "changes, and publish the changes to a specified Pypi repository."
    user_options = (
        ("version=", "v", "new version number"),
        ("config=", "c", "a config file with a release section"),
        ("description=", "d", "a description of the work done in the release")
    )

    def initialize_options(self):
        self.old_version = None     # the previous version
        self.version = None         # the new version
        self.config = "setup.cfg"   # path to configuration file with "release" section
        self.release_config = None  # an instance of a ReleaseConfig
        self.changelog_file = None  # path to a changelog file
        self.description = None     # description text

    def finalize_options(self):
        if not os.path.exists(self.config):
            raise IOError(
                "Specified release config file ({}) does not exist".format(self.release_config))

        self.release_config = ReleaseConfig.load(self.config)

        if not os.path.exists(self.release_config.version_file):
            raise IOError(
                "Specified version file ({}) does not exist".format(
                    self.release_config.version_file))

        if not os.path.exists(self.release_config.changelog_file):
            raise IOError(
                "Specified changelog file ({}) does not exist".format(
                    self.release_config.changelog_file))

        self.old_version = current_version_from_version_file(self.release_config.version_file)
        self.version = self.version or bump_patch_version(self.old_version)
        self.changelog_file = self.release_config.changelog_file
        self.description = self.description or get_description()

    def run(self):
        # fail fast if working tree is not clean
        if not is_tree_clean():
            print("Git working tree is not clean. Commit or stash uncommitted changes "
                  "before proceeding.")
            raise IOError()

        # update version specifier in module
        update_version_file(self.release_config.version_file, self.version)

        # commit changes
        commit_changes(self.version)

        # tag the release
        tag(self.version)

        # push changes to Github
        push_to_github = parse_y_n_response(
            input("Would you like to push the changes to master? [y/n] ").strip())

        if push_to_github:
            print("Pushing changes to Github")
            push()

        # build and publish
        build()
        publish_to_pypi()