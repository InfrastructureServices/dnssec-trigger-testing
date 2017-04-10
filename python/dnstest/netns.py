# Network namespaces
#
# Currently best-effort functions meaning no clean up after error.

import subprocess

from result import Result, ResultType


def _build_ret_value(ret):
    """
    Map subprocess.run() return value into my own Result type
    :param ret: Return value from call to subprocess.run() 
    :return: Value of type Result built from "ret"
    """
    if ret.returncode == 0:
        return Result(ResultType.Ok, None)
    else:
        return Result(ResultType.Err, ret.stderr)


def _run_ip_command(command):
    """
    :param command: List of strings 
    :return: 
    """
    return subprocess.run(["ip"] + command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _run_ip_ns_command(ns, command):
    """
    :param ns: Namespace 
    :param command: List of strings
    :return: 
    """
    return _run_ip_command(["netns", "exec", ns, "ip"] + command)


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
    ret = subprocess.run(["ip", "netns", "add", name], stderr=subprocess.PIPE)
    return _build_ret_value(ret)


def connect_to_root_ns(name):
    """
    Create a new veth pair, connect one side to the root and the second one to the NAME namespace.
    :param name: Name of the namespace to be connected to the root ns
    :return: Value of type Result containing either None or a string with error message 
    """
    root_link_name = _root_link_name(name)
    ns_link_name = _ns_link_name(name)
    ret = subprocess.run(["ip", "link", "add", root_link_name, "type", "veth", "peer", "name", ns_link_name],
                         stderr=subprocess.PIPE)
    if ret.returncode == 0:
        ret = subprocess.run(["ip", "link", "set", ns_link_name, "netns", name],
                             stderr=subprocess.PIPE)

    return _build_ret_value(ret)


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
    root_cmds = [["addr", "add", root_ip, "dev", root_link_name],
                 ["link", "set", root_link_name, "up"]]
    ns_cmds = [["addr", "add", ns_ip, "dev", ns_link_name],
               ["link", "set", ns_link_name, "up"]]
    for i in root_cmds:
        ret = _run_ip_command(i)
        if ret.returncode != 0:
            return _build_ret_value(ret)

    for i in ns_cmds:
        ret = _run_ip_ns_command(name, i)
        if ret.returncode != 0:
            return _build_ret_value(ret)

    return Result(ResultType.Ok, None)


def get_ns_list():
    """
    Get a list of namespaces available on this system.
    :return: Result type containing either a list of namespaces or a string with error message
    """
    ret = subprocess.run(["ip", "netns"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = None
    if ret.returncode == 0:
        ns_list_text = ret.stdout.decode("UTF-8")
        ns_list = ns_list_text.splitlines()
        result = Result(ResultType.Ok, ns_list)
    else:
        result = Result(ResultType.Err, ret.stderr)

    return result


def get_ns_dev_addr(name):
    """
    ip -4 a show dev veth-root-ns1 scope global | grep -E "[0-9]*\.[0-9]*\.[0-9]*\.[0-9]*/[0-9]*"
    :param name: 
    :return: 
    """
    pass
