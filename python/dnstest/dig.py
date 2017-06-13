
import subprocess
import re


class DigBuilder:
    def __init__(self, name, server=None, type=None):
        self.name = name
        self.server = server
        self.type = type

    def run(self):
        arguments = []
        if self.server is not None:
            arguments.append("@"+self.server)
        if self.name is not None:
            arguments.append(self.name)
        if self.type is not None:
            arguments.append(self.type)
        ret = subprocess.run(["dig"] + arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if ret.returncode != 0:
            pass
        else:
            comment = re.compile(r'^;')
            output_lines = ret.stdout.decode("UTF-8").split('\n')
            a_record = re.compile(r'IN\s+A')
            all_records = list(filter(lambda l: not comment.search(l), output_lines))
            desired_records = list(filter(a_record.search, all_records))
            # list(map(print, desired_records))
            return desired_records
