#!/usr/bin/python3
"""vcustomer.py - spinning up docker instances from the my-amsix api.

Usage:
  vcustomer.py --create (quarantine|isp) <docker_api> <docker_net> <link-id>
  vcustomer.py --convert (quarantine|isp) <docker_api> <link-id>
  vcustomer.py --execute (foreground|background) <docker_api> <link-id> <command>
  vcustomer.py --init-net <docker_api> <docker_net> <docker_phys> <link-id>
  vcustomer.py --list <docker_api>
  vcustomer.py --list-net <docker_api>
  vcustomer.py --remove <docker_api> <link-id>
  vcustomer.py --remove-net <docker_api> <docker_net>
  vcustomer.py --wipe <docker_api>

Options:
  -h --help     Show this screen.
  --version     Show version.

Author: Joris Claassen

"""
from docopt import docopt
from netaddr import *
import hashlib
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

def CreateVlan(ip):
	iphash = hashlib.sha256(ip.encode()).hexdigest()
	if int(iphash, 16)%10000 < 4090:
		vlan = int(iphash, 16)%10000
		return vlan
	else:
		vlan = int(iphash, 16)%1000
		return vlan

def ConvertTo(target):
	FlushAddress()
	link = myamsix_rest.GetLink(myamsix_api,args["<link-id>"])
	# extract production ipv4 ip
	for router in link["vlans"][0]["routers"]:
		if router["class"].startswith("Ipv4"):
			ispip = IPNetwork(router["ip"] + "/" + str(router["netmask"]))
	# extract quarantine ipv4 ip
	addr = link["vlans"][0]["routers"][0]["quarantine"]["address"]
	subnet = link["vlans"][0]["routers"][0]["quarantine"]["netmask"]
	qip = IPNetwork(str(addr) + "/" + str(subnet))
	print(CreateVlan(str(ispip.ip)))
	if target == "isp":
		AddAddress(str(ispip.ip), str(ispip.prefixlen))
		AddRoute(str(ispip.network), str(ispip.prefixlen))
	elif target == "quarantine":
		AddAddress(str(qip.ip), str(qip.prefixlen))
		AddRoute(str(qip.network), str(qip.prefixlen))
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
	addr = link["vlans"][0]["routers"][0]["quarantine"]["address"]
	subnet = link["vlans"][0]["routers"][0]["quarantine"]["netmask"]
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

#list all running containers on this server
if args["--list"]:
	containers = docker_rest.InspectContainer(args["<docker_api>"])
	for vcustomer in containers:
		print(str(vcustomer["Names"][0])[1:])

if args["--list-net"]:
	networks = docker_rest.InspectNet(args["<docker_api>"])
	for network in networks:
		print(network["Name"])

# stop and remove docker container
if args["--remove"]:
	print(docker_rest.StopContainer(args["<docker_api>"], args["<link-id>"]))
	print(docker_rest.RemoveContainer(args["<docker_api>"], args["<link-id>"]))

# remove docker network
if args["--remove-net"]:
	print(docker_rest.RemoveNet(args["<docker_api>"], args["<docker_net>"]))

# wipe all containers and networks
if args["--wipe"]:
	containers = docker_rest.InspectContainer(args["<docker_api>"])
	for vcustomer in containers:
		print(docker_rest.StopContainer(args["<docker_api>"],(str(vcustomer["Names"][0])[1:])))
		print(docker_rest.RemoveContainer(args["<docker_api>"], (str(vcustomer["Names"][0])[1:])))
	networks = docker_rest.InspectNet(args["<docker_api>"])
	for network in networks:
		print(docker_rest.RemoveNet(args["<docker_api>"], str(network["Name"])))
