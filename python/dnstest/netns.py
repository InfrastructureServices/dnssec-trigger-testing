# Network namespaces
#
# Currently best-effort functions meaning no clean up after error.

import subprocess
import re

from error import ConfigError


def _run_ip_command(arguments):
    """
    :param arguments: List of strings
    :return: 
    """
    ret = subprocess.run(["ip"] + arguments, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ret.returncode != 0:
        raise ConfigError("ip", arguments, ret.stderr.decode("UTF-8"))
    else:
        return ret


def _run_ip_ns_command(ns, arguments):
    """
    :param ns: Namespace 
    :param arguments: List of strings
    :return: 
    """
    args_within_ns = ["netns", "exec", ns, "ip"] + arguments
    ret = _run_ip_command(args_within_ns)
    if ret.returncode != 0:
        raise ConfigError("ip", args_within_ns, ret.stderr.decode("UTF-8"))
    else:
        return ret


def _root_link_name(name):
    return "veth-root-" + name


def _ns_link_name(name):
    return "veth-" + name + "-root"


def new_namespace(name):
    """
    Create a new network namespace
    :param name: Name of the new namespace
    :return: Value of type Result containing either None or a string with error message
    """
    _run_ip_command(["netns", "add", name])


def connect_to_root_ns(name):
    """
    Create a new veth pair, connect one side to the root and the second one to the NAME namespace.
    :param name: Name of the namespace to be connected to the root ns
    :return: Value of type Result containing either None or a string with error message 
    """
    root_link_name = _root_link_name(name)
    ns_link_name = _ns_link_name(name)
    _run_ip_command(["link", "add", root_link_name, "type", "veth", "peer", "name", ns_link_name])
    _run_ip_command(["link", "set", ns_link_name, "netns", name])


def assign_addresses(name, id):
    """
    Assign IPv4 addresses to the link from root to NAME namespace. IP address will be 10.id.1.{1,2}
    :param name: Namespace name as a string
    :param id: Address ID as a number
    :return: Result sth 
    """
    root_ip = "100." + str(id) + ".1.1/24"
    ns_ip = "100." + str(id) + ".1.2/24"
    root_link_name = _root_link_name(name)
    ns_link_name = _ns_link_name(name)

    # Commands to run under root namespace
    root_cmds = [["addr", "add", root_ip, "dev", root_link_name],
                 ["link", "set", root_link_name, "up"]]
    for cmd in root_cmds:
        _run_ip_command(cmd)

    # Commands to run under specified namespace
    ns_cmds = [["addr", "add", ns_ip, "dev", ns_link_name],
               ["link", "set", ns_link_name, "up"]]
    for cmd in ns_cmds:
        _run_ip_ns_command(name, cmd)


def get_ns_list():
    """
    Get a list of namespaces available on this system.
    :return: Result type containing either a list of namespaces or a string with error message
    """
    ret = _run_ip_command(["netns"])
    ns_list_text = ret.stdout.decode("UTF-8")
    ns_list = ns_list_text.splitlines()
    return ns_list


def get_ns_dev_addr(name):
    """
    ip -4 a show dev veth-root-ns1 scope global | grep -E "[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*/[0-9]*"
    :param name: 
    :return: 
    """
    link = _ns_link_name(name)
    ret = _run_ip_ns_command(name, ["-4", "a", "show", "dev", link, "scope", "global"])
    out = ret.stdout.decode("UTF-8")
    ip = re.findall(r'[0-9]+(?:\.[0-9]+){3}', out)
    if len(ip) == 1:
        return ip[0]
    elif len(ip) > 1:
        # fixme: not sure what to do in this case
        return ip[0]
    else:
        return None

