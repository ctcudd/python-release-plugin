import os
import shutil
import tempfile
import unittest
from datetime import datetime

from pyreleaseplugin.docker_command import DockerCommand

THIS_DIR = os.path.dirname(os.path.abspath(__file__))


class TestDocker(unittest.TestCase):

    def test_docker_images(self):
        d = DockerCommand()
        images = d.list_images()
        for image in images:
            d.remove_image(image.id, True)

    def test_docker_build_image(self):
        d = DockerCommand()
        image = d.build_image(os.path.join(THIS_DIR, 'resources'), {}, 'test')
        print image



