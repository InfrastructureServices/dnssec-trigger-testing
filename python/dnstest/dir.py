# Create run configuration

import os


class Dir:
    base = "/tmp"

    @classmethod
    def init(cls):
        cls.base = os.getcwd() + "/run"
        os.mkdir(cls.base)

    @classmethod
    def new_dir(cls, name):
        path = cls.base + "/" + name
        os.mkdir(path)
        return path
