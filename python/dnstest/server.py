# Spin up DNS servers (either authoritative or recursive)
# TODO: implement

from jinja2 import Environment, FileSystemLoader
from enum import Enum
from dir import Dir

import os


class DNSServerType(Enum):
    AUTHORITATIVE = 1
    RESOLVER = 2


class DNSServer:
    def __init__(self, srv_type, interface):
        self.srv_type = srv_type
        self.interface = interface
        self.conf_path = Dir.new_dir("srv."+interface.get_address())
        j2_env = Environment(loader=FileSystemLoader(os.getcwd() + "/templates"))
        conf_file_content = j2_env.get_template("named.conf").render(
            ip_address = interface.get_address(),
            working_dir=self.conf_path,
            recursion="no"
        )
        with open(self.conf_path+"/named.conf", "w") as f:
            f.write(conf_file_content)

    def serve_zone(self, name):
        filename=name if name != "." else "root"
        j2_env = Environment(loader=FileSystemLoader(os.getcwd() + "/templates"))
        conf_file_content = j2_env.get_template("zone.conf").render(
            zone=name,
            filename=filename
        )
        with open(self.conf_path+"/named.conf", "a") as f:
            f.write(conf_file_content)

        name_for_servers = name if name != "." else "" # Just to avoid ".." at the end of these strings
        zone_file_content = j2_env.get_template("template.zone").render(
            primary_server="a."+name_for_servers,
            secondary_server="b."+name_for_servers,
            admin_email="admin.a."+name_for_servers,
            zone=name
        )
        with open(self.conf_path+"/"+filename+".zone", "w") as f:
            f.write(zone_file_content)

    def sign_zone(self, tld):
        pass

    def run(self):
        self.interface.run_command(["named", "-u", "root", "-c", self.conf_path+"/named.conf"])
