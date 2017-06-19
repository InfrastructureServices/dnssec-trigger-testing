# dnssec-trigger-testing

Testing suite for the DNSSEC trigger project.

## Idea:

 * Run Vagrant box with testing setup where
   * Authoritative DNS servers are running
   * Recursive resolvers with different DNSSEC setup are running
 * Compile latest dnssec-trigger from sources
 * Replace unbound-control with simple script to capture output
 * Send input to a running instance of dnssec-trigger as JSON and watch the output

## TODO list:

 * Create a Python wrapper for dnssec-trigger
 * Test very simple use case with only one working and broken resolver
 * Pick up testing framework and use it instead of hand-written scripts

## How to test:

```bash
$ vagrant up
$ vagrant ssh
$ dnssec-testing-test-unsecure
```

## Resources:

 * Network namespaces: http://blogs.igalia.com/dpino/2016/04/10/network-namespaces/ 
