#!/usr/bin/python3
"""test.py - spinning up docker instances from the my-amsix api.

Usage:
  test.py --create (quarantine|isp) <docker_api> <docker_net> <link-id>

Options:
  -h --help     Show this screen.
  --version     Show version.

Author: Joris Claassen

"""
from docopt import docopt
from netaddr import *
import json
import docker_rest
import myamsix_rest

args = docopt(__doc__, version='vcustomer.py 0.0.1')

myamsix_api="http://my.ams-ix.net"
#myamsix_api="http://my-staging.lab.ams-ix.net"

# create and start docker container based on myamsix link id
if args["--create"]:
	json_link = myamsix_rest.GetLink(myamsix_api,args["<link-id>"])
	for router in json_link["vlans"][0]["routers"]:
		if router["class"].startswith("Ipv4"):
			print(router["ip"])
