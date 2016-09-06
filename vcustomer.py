#!/usr/bin/python3
"""vcustomer.py - spinning up docker instances from the my-amsix api.

Usage:
  vcustomer.py --create (quarantine|isp) <docker_api> <docker_net> <link-id>
  vcustomer.py --convert (quarantine|isp) <docker_api> <link-id>
  vcustomer.py --execute (foreground|background) <docker_api> <link-id> <command>
  vcustomer.py --init-net <docker_api> <docker_net> <docker_phys> <link-id>
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

def AddAddress(ip, subnet):
	Execute("ip addr add " + ip + "/" + subnet + " dev eth0")

def AddRoute(network, subnet):
	Execute("ip route add " + network + "/" + subnet + " via dev eth0")

def CreateQuarantine():
	link = myamsix_rest.GetLink(myamsix_api,args["<link-id>"])
	addr = link["vlans"][0]["routers"][0]["quarantine"]["address"]
	subnet = link["vlans"][0]["routers"][0]["quarantine"]["netmask"]
	create = docker_rest.CreateContainer(args["<docker_api>"], args["<link-id>"], args["<docker_net>"], addr)
	data = json.loads(create.content.decode())
	try:
		assert create.status_code == 201
		print("Container created succesfully!")
		print(docker_rest.StartContainer(args["<docker_api>"], data["Id"])) 
	except AssertionError:
		print("Container not created succesfully:\n\n"
			+ data["message"])
def ConvertTo(target):
	FlushAddress()
	link = myamsix_rest.GetLink(myamsix_api,args["<link-id>"])
	if target == "isp":
		for router in link["vlans"][0]["routers"]:
			if router["class"].startswith("Ipv4"):
				ip = IPNetwork(router["ip"] + "/" + str(router["netmask"]))
	elif target == "quarantine":
		addr = link["vlans"][0]["routers"][0]["quarantine"]["address"]
		subnet = link["vlans"][0]["routers"][0]["quarantine"]["netmask"]
		ip = IPNetwork(str(addr) + "/" + str(subnet))
	AddAddress(str(ip.ip), str(ip.prefixlen))
	AddRoute(str(ip.network), str(ip.prefixlen))
	print("Container " + args["<link-id>"] + " succesfully converted to " + target + " vlan.")
	
def Execute(command=args["<command>"]):
	action = "bg"
	if args["foreground"]:
		action = "fg"
	print(docker_rest.StartExec(args["<docker_api>"], docker_rest.CreateExec(args["<docker_api>"], args["<link-id>"], command), action).text)

def FlushAddress():
	Execute("ip addr flush dev eth0")

def InitNet():
	link = myamsix_rest.GetLink(myamsix_api,args["<link-id>"])
	addr = link["vlans"][0]["quarantine"]["address"]
	subnet = link["vlans"][0]["quarantine"]["netmask"]
	ip = IPNetwork(str(addr) + "/" + str(subnet))
	print(docker_rest.InspectNet(args["<docker_api>"], docker_rest.CreateNet(args["<docker_api>"], args["<docker_net>"], args["<docker_phys>"], str(ip.network), str(ip.prefixlen))))

#myamsix_api="http://my.ams-ix.net"
myamsix_api="http://my-staging.lab.ams-ix.net"

# create and start docker container based on myamsix link id
if args["--create"]:
	CreateQuarantine()
	if args["isp"]:
		ConvertTo("isp")

# convert ip settings to isp or quarantine
if args["--convert"]:
	if args["isp"]:
		ConvertTo("isp")
	if args["quarantine"]:
		ConvertTo("quarantine")

# execute command in container
if args["--execute"]:
	Execute()

# initialize docker network based on the ip and subnet received from the myamsix api
if args["--init-net"]:
	InitNet()

# stop and remove docker container
if args["--remove"]:
	print(docker_rest.StopContainer(args["<docker_api>"], args["<link-id>"]))
	print(docker_rest.RemoveContainer(args["<docker_api>"], args["<link-id>"]))

# remove docker network
if args["--remove-net"]:
	print(docker_rest.RemoveNet(args["<docker_api>"], args["<docker_net>"]))
