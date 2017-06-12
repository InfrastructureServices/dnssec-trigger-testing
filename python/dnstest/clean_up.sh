#!/bin/bash

pgrep named | xargs kill
ip -all netns delete
rm -rf /tmp/run/
