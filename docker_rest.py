# Docker REST API module
import requests
import json

# function to retreive network information from the docker API
def InspectNet(rest_api, net_name=""):
	if net_name == "":
		r = requests.get(rest_api + "/networks/")
	else:
		r = requests.get(rest_api + "/networks/" + net_name)
	try:
		assert r.status_code == 200
		return r.json()
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text

# function to retrieve container information from the docker API
def InspectCont(rest_api, cont_name=""):
	if cont_name == "":
		r = requests.get(rest_api + "/containers/json?all=1")
	else:
		r = requests.get(rest_api + "/containers/" + cont_name + "/json")
	try:
		assert r.status_code == 200
		return r.json()
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text

# function to create a new network using the docker API
def CreateNet(rest_api, net_name, parent_if):
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
	try:
		assert r.status_code == 201
		return r.json()
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text

# function to create a new container using the docker API
def CreateCont(rest_api, name, net_name, ip="", mac=""):
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
	try:
		assert r.status_code == 201
		return r.json()
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text

# function to create an excute command for an container
def CreateExec(rest_api, name, cmd):
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
	try:
		assert r.status_code == 201
		data = json.loads(r.content.decode())
		return(data["Id"])
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text

# function to delete a network using the docker API
def RemoveNet(rest_api, name):
	r = requests.delete(rest_api + "/networks/" + name)
	try:
		assert r.status_code == 204
		return "Network removed succesfully!"
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text

# function to kill and delete a container using the docker API
def RemoveCont(rest_api, name):
	r = requests.delete(rest_api + "/containers/" + name)
	try:
		assert r.status_code == 204
		return "Container removed succesfully!"
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text

# function to start an execute command in an container
def StartExec(rest_api, id):
	payload = {
			"Detach": False,
			"Tty": False
		}
	headers = {"content-type": "application/json"}
	r = requests.post(rest_api + "/exec/" + id + "/start", data=json.dumps(payload), headers=headers)
	try:
		assert r.status_code == 200
		return r.__dict__
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text

# function to start a container using the docker API
def StartCont(name):
	r = requests.post(rest_api + "/containers/" + name + "/start")
	try:
		assert r.status_code == 204
		return "Container started succesfully!"
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text

def StopCont(name):
	r = requests.post(rest_api + "/containers/" + name + "/stop")
	try:
		assert r.status_code == 204
		return "Container stopped succesfully!"
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text
