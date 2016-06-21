#!/usr/bin/python3
"""request.py - sending REST requests to the docker API.

Usage:
  request.py get network <net_name>
  request.py get container [-a --all]
  request.py create network <net_name> <parent_if>
  request.py create container <name> <net_name> [<ip> <mac>]
  request.py start container <name>

Options:
  -h --help     Show this screen.
  --version     Show version.

"""
import json
from docopt import docopt 
import urllib.request as urllib2
import requests

# the url of the docker REST API
rest_api = "http://lamstix.lab.ams-ix.net:2375"

# function to retreive network information from the docker API
def get_net(net_name):
	rnet = requests.get(rest_api + "/networks/" + net_name)
	return rnet.json()

# function to retrieve container information from the docker API
def get_cont():
	rcont = requests.get(rest_api + "/containers/json")
	return rcont.json()

# function to create a new network using the docker API
def create_net(net_name, parent_if):
	payload = {
			"Name": net_name,
			"CheckDuplicate": True,
			"Driver": "macvlan",
			"EnableIPv6": False,
			"IPAM": {
				"Config": [{
					"Subnet": "10.25.208.0/21"}]
				},
			"Options": {"parent": parent_if}
		} 
	
	headers = {"content-type": "application/json"}
	response = requests.post(rest_api + "/networks/create", data=json.dumps(payload), headers=headers)	
	print(response.text)

# function to create a new container using the docker API
def create_cont(name, net_name, ip, mac):
	payload = {
			"Hostname": name,
			"AttachStdin": False,
			"AttachStdout": False,
			"AttachStderr": False,
			"Tty": True,
			"OpenStdin": True,
			"StdinOnce": False,
			"Cmd": [
				"/bin/sh"
			],
			"Image": "alpine",
			"NetworkDisabled": False,
			"MacAddress": mac,
			"HostConfig": {
				"NetworkMode": net_name
			},
			"NetworkingConfig": {
				"EndpointsConfig": {
					net_name: {
						"IPAMConfig": {
							"IPv4Address": ip
						}
					}
				}
			}
		}
	headers = {"content-type": "application/json"}
	response = requests.post(rest_api + "/containers/create?name=" + name, data=json.dumps(payload), headers=headers)
	
	print(rest_api + "/containers/create?name=" + name)
	print(headers)
	print(json.dumps(payload, sort_keys=True, indent=4, separators=(',', ': ')))
	print(response.text)

# function to start a container using the docker API
def start_cont(name):
	response = requests.post(rest_api + "/containers/" + name + "/start")
	print(response.text)

# main program
args = docopt(__doc__, version='request.py 0.0.1')

if args["get"] and args["network"]:
	print(json.dumps(get_net(args["<net_name>"]), sort_keys=True, indent=4, separators=(',', ': ')))	

if args["get"] and args["container"]:
	print(json.dumps(get_cont(), sort_keys=True, indent=4, separators=(',', ': ')))

if args["create"] and args["network"]:
	create_net(args["<net_name>"], args["<parent_if>"])

if args["create"] and args["container"]:
	create_cont(args["<name>"], args["<net_name>"], args["<ip>"], args["<mac>"])

if args["start"] and args["container"]:
	start_cont(args["<name>"])
