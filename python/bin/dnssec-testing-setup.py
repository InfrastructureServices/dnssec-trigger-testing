#!/usr/bin/env python3

import netns as ns

ns.new_namespace("ns1")
ns.new_namespace("ns2")

ns.connect_to_root_ns("ns1")
ns.connect_to_root_ns("ns2")

ns.assign_addresses("ns1", 1)
ns.assign_addresses("ns2", 2)

ns.get_ns_list()
