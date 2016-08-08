#!/usr/bin/python3
"""vcustomer.py - spinning up docker instances from the my-amsix api.

Usage:
  vcustomer.py --create-quarantine <docker_api> <docker_net> <link-id> [prod]
  vcustomer.py --execute-quarantine <docker_api> <link-id> (ping) [prod] 
  vcustomer.py --init-net-quarantine <docker_api> <docker_net> <docker_phys> <link-id> [prod]
  vcustomer.py --remove <docker_api> <link-id>
  vcustomer.py --remove-net <docker_api> <docker_net>

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

if args["prod"]:
	myamsix_api="http://my.ams-ix.net"
else:
	myamsix_api="http://my-staging.lab.ams-ix.net"

# create and start docker container based on myamsix link id
if args["--create-quarantine"]:
	json_link = myamsix_rest.GetLink(myamsix_api,args["<link-id>"])
	qaddr = json_link["vlans"][0]["quarantine"]["address"]
	qsubnet = json_link["vlans"][0]["quarantine"]["netmask"]
	create = docker_rest.CreateContainer(args["<docker_api>"], args["<link-id>"], args["<docker_net>"], qaddr)
	data = json.loads(create.content.decode())
	try:
		assert create.status_code == 201
		print("Container created succesfully!")
		print(docker_rest.StartContainer(args["<docker_api>"], data["Id"])) 
	except AssertionError:
		print("Container not created succesfully:\n\n"
			+ data["message"])

# execute command on quarantine
if args["--execute-quarantine"]:
	json_link = myamsix_rest.GetLink(myamsix_api,args["<link-id>"])
	qaddr = json_link["vlans"][0]["quarantine"]["address"]
	qsubnet = json_link["vlans"][0]["quarantine"]["netmask"]
	qping = json_link["vlans"][0]["quarantine"]["ping_against_ip"]
	if args["ping"]:
		print(docker_rest.StartExec(args["<docker_api>"], docker_rest.CreateExec(args["<docker_api>"], args["<link-id>"], "ping -c 3600 " + qping)))

# initialize docker network based on the ip and subnet received from the myamsix api
if args["--init-net-quarantine"]:
	json_link = myamsix_rest.GetLink(myamsix_api,args["<link-id>"])
	qaddr = json_link["vlans"][0]["quarantine"]["address"]
	qsubnet = json_link["vlans"][0]["quarantine"]["netmask"]
	qip = IPNetwork(str(qaddr) + "/" + str(qsubnet))

	#print(docker_rest.CreateNet(args["<docker_api>"], args["<docker_net>"], args["<docker_phys>"], str(qip.network), str(qip.prefixlen)))
	print(docker_rest.InspectNet(args["<docker_api>"], docker_rest.CreateNet(args["<docker_api>"], args["<docker_net>"], args["<docker_phys>"], str(qip.network), str(qip.prefixlen))))



# stop and remove docker container
if args["--remove"]:
	print(docker_rest.StopContainer(args["<docker_api>"], args["<link-id>"]))
	print(docker_rest.RemoveContainer(args["<docker_api>"], args["<link-id>"]))

# remove docker network
if args["--remove-net"]:
	print(docker_rest.RemoveNet(args["<docker_api>"], args["<docker_net>"]))
