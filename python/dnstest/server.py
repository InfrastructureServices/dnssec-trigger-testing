# Spin up DNS servers (either authoritative or recursive)

from jinja2 import Environment, PackageLoader, FileSystemLoader
from enum import Enum
from pkg_resources import resource_filename
from dnstest.dir import Dir

import subprocess
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
        self.filename = "foobar"
        self.zonefilename = "foobar"
        self.dsfilename = "foobar"
        self.ksk_file = "foobar"
        self.zone = "foobar"
        self.conf_path = Dir.new_dir("srv."+interface.get_address())
        j2_env = Environment(loader=PackageLoader(__name__, 'templates'))
        conf_file_content = j2_env.get_template("named.conf").render(
            ip_address = interface.get_address(),
            working_dir=self.conf_path,
            recursion="no" if srv_type == DNSServerType.AUTHORITATIVE else "yes"
        )
        with open(self.conf_path+"/named.conf", "w") as f:
            f.write(conf_file_content)
        if srv_type == DNSServerType.RESOLVER:
            shutil.copyfile(resource_filename(__name__, 'templates/root.hint'), self.conf_path+"/root.hint")
            with open(self.conf_path+"/named.conf", "a") as f:
                f.write(RESOLVER_HINT)

    @staticmethod
    def __ns_names(zone_name):
        name_for_servers = zone_name if zone_name != "." else "" # Just to avoid ".." at the end of these strings
        return "a."+name_for_servers, "b."+name_for_servers, "admin.a."+name_for_servers

    def serve_zone(self, name):
        self.zone = name
        self.filename=name[:-1] if name != "." else "root"
        self.zonefilename = self.filename+".zone"
        self.dsfilename = "dsset-" + self.zone
        j2_env = Environment(loader=PackageLoader(__name__, 'templates'))
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
        j2_env = Environment(loader=PackageLoader(__name__, 'templates'))
        zone_file_content = j2_env.get_template("delegation.zone").render(
            primary_server = prim,
            secondary_server = second,
            zone=zone,
            ip_address=server_ip_address
        )
        with open(self.conf_path+"/"+self.filename+".zone", "a") as f:
            f.write(zone_file_content)

    def insert_ds_keys(self, zone):
        """
        Insert DS RR from delegated zone
        :param zone: zone object
        :type zone: DNSServer
        :return:
        """
        with open(self.conf_path+"/"+self.filename+".zone", "a") as zonefile:
            with open(zone.conf_path+"/"+zone.dsfilename, "r") as dsfile:
                zonefile.write(dsfile.read())

    def sign_zone(self):#, tld):
        """
        Generate ZSK and KSK with dnssec-keygen
        Sign with dnssec-signzone
        """
        subprocess.run(["dnssec-keygen", "-f", "KSK", "-n", "ZONE", self.zone], cwd=self.conf_path)
        self.ksk_file = list(filter(lambda l: l.endswith("key"), os.listdir(self.conf_path)))[0]
        subprocess.run(["dnssec-keygen", "-n", "ZONE", self.zone], cwd=self.conf_path)
        key_files = list(filter(lambda l: l.endswith("key"), os.listdir(self.conf_path)))
        with open(self.conf_path+"/"+self.filename+".zone", "a") as f:
            for k in key_files:
                f.write("$INCLUDE " + k + "\n")
        subprocess.run(["dnssec-signzone", "-A", "-N", "INCREMENT", "-o", self.zone, "-t", self.filename+".zone"], cwd=self.conf_path)

    def insert_trust_anchor(self, root_server):
        """
        Insert KSK of the root server
        :param root_server:
        :type root_server: DNSServer
        :return:
        """
        if self.srv_type == DNSServerType.RESOLVER:
            with open(root_server.conf_path+"/"+root_server.ksk_file, "r") as root_key_file:
                root_key = root_key_file.readlines()[-1][20:-1]
                with open(self.conf_path+"/named.conf", "a") as config:
                    config.write("managed-keys {\n")
                    config.write("\".\" initial-key 257 3 5 \"")
                    config.write(root_key)
                    config.write("\";\n};\n")

    def run(self):
        self.interface.run_command(["named", "-u", "root", "-c", self.conf_path+"/named.conf"])
