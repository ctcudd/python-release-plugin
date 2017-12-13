import os
import shutil
import tempfile
import unittest
from datetime import datetime

from pyreleaseplugin.git import get_current_branch, get_current_commit_sha

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestDocker(unittest.TestCase):

    def test_get_current_branch(self):
        branch = get_current_branch()
        print branch

    def test_docker_build_image(self):
        sha = get_current_commit_sha()
        print sha



