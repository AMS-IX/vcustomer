#!/usr/bin/python3
"""vcustomer.py - spinning up docker instances from the my-amsix api.

Usage:
  vcustomer.py create <docker_api> <docker_if> (prod|staging) <link-id> 
  vcustomer.py remove <docker_api> <link-id>

Options:
  -h --help     Show this screen.
  --version     Show version.

Author: Joris Claassen

"""
from docopt import docopt
import docker_rest
import myamsix_rest

args = docopt(__doc__, version='vcustomer.py 0.0.1')

if args["prod"]:
	myamsix_api="http://my.ams-ix.net"
elif args["staging"]:
	myamsix_api="http://my-staging.lab.ams-ix.net"

#if args["<docker_api>]" == "lamstix":
	#args["<docker_api>"]="http://lamstix.lab.ams-ix.net:2375"

def CreateVCustomer():
	json_link = myamsix_rest.GetLink(myamsix_api,args["<link-id>"])
	qaddr = json_link["vlans"][0]["quarantine"]["address"]
	qsubnet = json_link["vlans"][0]["quarantine"]["netmask"]
	qping = json_link["vlans"][0]["quarantine"]["ping_against_ip"]

	print(docker_rest.InspectNet(args["<docker_api>"], args["<docker_if>"]))
	print(docker_rest.InspectContainer(args["<docker_api>"], args["<link-id>"]))

	docker_rest.CreateContainer(args["<docker_api>"], args["<link-id>"], args["<docker_if>"], qaddr)
	docker_rest.StartContainer(args["<docker_api>"], args["<link-id>"]) 

	docker_rest.StartExec(args["<docker_api>"], docker_rest.CreateExec(args["<docker_api>"], args["<link-id>"], "ping -c 3600 " + qping))

def RemoveVCustomer():
	docker_rest.StopContainer(args["<docker_api>"], args["<link-id>"])
	docker_rest.RemoveContainer(args["<docker_api>"], args["<link-id>"])

if args["create"]:
        CreateVCustomer()

if args["remove"]:
	RemoveVCustomer()
