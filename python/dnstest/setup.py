#!/usr/bin/python3

from dnstest.server import DNSServer,DNSServerType
from dnstest.netns import NetworkInterface
from dnstest.dir import Dir
from dnstest.error import ConfigError


def main():
    try:
        # Init directory tree
        Dir.init()

        # Set up root server
        ni_root = NetworkInterface("root", 1)
        root_server = DNSServer(DNSServerType.AUTHORITATIVE, ni_root)
        root_server.serve_zone(".")

        # com. authoritative server
        ni_com = NetworkInterface("com", 2)
        com_server = DNSServer(DNSServerType.AUTHORITATIVE, ni_com)
        com_server.serve_zone("com.")

        root_server.delegate_zone("com.", ni_com.get_address())

        # example.com. authoritative server
        ni_example = NetworkInterface("exp", 3)
        example_com_server = DNSServer(DNSServerType.AUTHORITATIVE, ni_example)
        example_com_server.serve_zone("example.com.")

        com_server.delegate_zone("example.com.", ni_example.get_address())

        # Start signing zones
        example_com_server.sign_zone()
        com_server.insert_ds_keys(example_com_server)
        com_server.sign_zone()
        root_server.insert_ds_keys(com_server)
        root_server.sign_zone()

        # Resolver - no validation yet!
        ni_resolver = NetworkInterface("res", 99)
        resolver = DNSServer(DNSServerType.RESOLVER, ni_resolver)
        resolver.insert_trust_anchor(root_server)

        root_server.run()
        com_server.run()
        example_com_server.run()
        resolver.run()
    except ConfigError as err:
        print("error: {0}".format(err))


if __name__ == '__main__':
    main()
