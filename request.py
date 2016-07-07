#!/usr/bin/python3
"""request.py - sending REST requests to the docker API.

Usage:
  request.py inspect network [<net_name>]
  request.py inspect container [<name>]
  request.py create network <net_name> <parent_if>
  request.py create container <name> <net_name> [<ip> <mac>]
  request.py delete network <net_name>
  request.py delete container <name>
  request.py start container <name>
  request.py stop container <name>
  request.py execute <container> <command>

Options:
  -h --help     Show this screen.
  --version     Show version.

Author: Joris Claassen

"""
import json
from docopt import docopt 
import urllib.request as urllib2
import requests

# the url of the docker REST API
rest_api = "http://lamstix.lab.ams-ix.net:2375"

# function to retreive network information from the docker API
def get_net():
	if args["<net_name>"]:
		r = requests.get(rest_api + "/networks/" + args["<net_name>"])
	else:
		r = requests.get(rest_api + "/networks/")
	return r.json()

# function to retrieve container information from the docker API
def get_cont():
	if args["<name>"]:
		r = requests.get(rest_api + "/containers/" + args["<name>"] + "/json")
	else:
		r = requests.get(rest_api + "/containers/json?all=1")
	return r.json()

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
			"Options": {
				"parent": parent_if,
				"macvlan_mode": "vepa"
			}
		} 
	
	headers = {"content-type": "application/json"}
	r = requests.post(rest_api + "/networks/create", data=json.dumps(payload), headers=headers)	
	if r.status_code is 201:
		print("Success!")
	else:
		print(r.text)

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
				"NetworkMode": net_name,
				"Privileged": True
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
	r = requests.post(rest_api + "/containers/create?name=" + name, data=json.dumps(payload), headers=headers)
	if r.status_code is 201:
		print("Success!")
	else:
		print(r.text)

# function to create an excute command for an container
def create_exec(name, cmd):
	payload = {
                        "AttachStdin": False,
                        "AttachStdout": True,
                        "AttachStderr": True,
			"DetachKeys": "ctrl-p,ctrl-q",
			"Tty": False,
			"Cmd": [
				"/bin/sh",
				"-c",
				cmd
			],
		}
	headers = {"content-type": "application/json"}
	r = requests.post(rest_api + "/containers/" + name + "/exec", data=json.dumps(payload), headers=headers)
	if r.status_code is 201:
		data = json.loads(r.content.decode())
		return(data["Id"])
	else:
		print(r.text)

# function to delete a network using the docker API
def del_net(name):
	r = requests.delete(rest_api + "/networks/" + name)
	if r.status_code is 204:
		print("Success!")
	else:
		print(r.text)

# function to kill and delete a container using the docker API
def del_cont(name):
	r = requests.delete(rest_api + "/containers/" + name)
	if r.status_code is 204:
		print("Success!")
	else:
        	print(r.text)

# function to start an execute command in an container
def start_exec(id):
	payload = {
			"Detach": False,
			"Tty": False
		}
	headers = {"content-type": "application/json"}
	r = requests.post(rest_api + "/exec/" + id + "/start", data=json.dumps(payload), headers=headers)
	print(r.text)

# function to start a container using the docker API
def start_cont(name):
	r = requests.post(rest_api + "/containers/" + name + "/start")
	if r.status_code is 204:
		print("Success!")
	else:
		print(r.text)

def stop_cont(name):
	r = requests.post(rest_api + "/containers/" + name + "/stop")
	if r.status_code is 204:
		print("Success!")
	else:
		print(r.text)

# main program
args = docopt(__doc__, version='request.py 0.0.1')

if args["inspect"] and args["network"]:
	print(json.dumps(get_net(), sort_keys=True, indent=4, separators=(',', ': ')))	

if args["inspect"] and args["container"]:
	print(json.dumps(get_cont(), sort_keys=True, indent=4, separators=(',', ': ')))

if args["create"] and args["network"]:
	create_net(args["<net_name>"], args["<parent_if>"])

if args["create"] and args["container"]:
	create_cont(args["<name>"], args["<net_name>"], args["<ip>"], args["<mac>"])

if args["delete"] and args["network"]:
	del_net(args["<net_name>"])

if args["delete"] and args["container"]:
	stop_cont(args["<name>"])
	del_cont(args["<name>"])

if args["start"] and args["container"]:
	start_cont(args["<name>"])

if args["stop"] and args["container"]:
	stop_cont(args["<name>"])

if args["execute"]:
	exec_id = create_exec(args["<container>"], args["<command>"])
	if exec_id:
		start_exec(exec_id)
