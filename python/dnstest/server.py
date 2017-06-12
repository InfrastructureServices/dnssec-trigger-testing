# Spin up DNS servers (either authoritative or recursive)

from jinja2 import Environment, FileSystemLoader
from enum import Enum
from dnstest.dir import Dir

import os
import shutil

RESOLVER_HINT = """

zone "." {
    type hint;
    file "root.hint";
};


"""


class DNSServerType(Enum):
    AUTHORITATIVE = 1
    RESOLVER = 2


class DNSServer:
    def __init__(self, srv_type, interface):
        self.srv_type = srv_type
        self.interface = interface
        self.conf_path = Dir.new_dir("srv."+interface.get_address())
        j2_env = Environment(loader=FileSystemLoader("templates"))
        conf_file_content = j2_env.get_template("named.conf").render(
            ip_address = interface.get_address(),
            working_dir=self.conf_path,
            recursion="no" if srv_type == DNSServerType.AUTHORITATIVE else "yes"
        )
        with open(self.conf_path+"/named.conf", "w") as f:
            f.write(conf_file_content)
        if srv_type == DNSServerType.RESOLVER:
            shutil.copyfile(os.getcwd()+"/templates/root.hint", self.conf_path+"/root.hint")
            with open(self.conf_path+"/named.conf", "a") as f:
                f.write(RESOLVER_HINT)

    @staticmethod
    def __ns_names(zone_name):
        name_for_servers = zone_name if zone_name != "." else "" # Just to avoid ".." at the end of these strings
        return "a."+name_for_servers, "b."+name_for_servers, "admin.a."+name_for_servers

    def serve_zone(self, name):
        self.filename=name if name != "." else "root"
        j2_env = Environment(loader=FileSystemLoader(os.getcwd() + "/templates"))
        conf_file_content = j2_env.get_template("zone.conf").render(
            zone=name,
            filename=self.filename
        )
        with open(self.conf_path+"/named.conf", "a") as f:
            f.write(conf_file_content)

        prim, second, admin = DNSServer.__ns_names(name)
        zone_file_content = j2_env.get_template("template.zone").render(
            primary_server = prim,
            secondary_server = second,
            admin_email= admin,
            zone=name,
            ip_address=self.interface.get_address()
        )
        with open(self.conf_path+"/"+self.filename+".zone", "w") as f:
            f.write(zone_file_content)

    def delegate_zone(self, zone, server_ip_address):
        prim, second, admin = DNSServer.__ns_names(zone)
        j2_env = Environment(loader=FileSystemLoader(os.getcwd() + "/templates"))
        zone_file_content = j2_env.get_template("delegation.zone").render(
            primary_server = prim,
            secondary_server = second,
            zone=zone,
            ip_address=server_ip_address
        )
        with open(self.conf_path+"/"+self.filename+".zone", "a") as f:
            f.write(zone_file_content)

    def sign_zone(self, tld):
        pass

    def run(self):
        self.interface.run_command(["named", "-u", "root", "-c", self.conf_path+"/named.conf"])
