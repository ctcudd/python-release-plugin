import docker


class DockerCommand(object):

    def __init__(self):
        self.client = docker.from_env()

    def list_containers(self):
        return self.client.containers.list()

    def list_images(self):
        return self.client.images.list()

    def remove_image(self, image_id, force=False):
        return self.client.images.remove(image_id, force)

    def build_image(self, dockerfile_dir, buildargs, tag):
        return self.client.images.build(path=dockerfile_dir, buildargs=buildargs, tag=tag)

