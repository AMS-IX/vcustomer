# Docker REST API module
import json
import requests

# function to create a new container using the docker API
def CreateContainer(rest_api, name, net_name, ip="", mac=""):
    payload = {
            "Hostname": name,
            "AttachStdin": False,
            "AttachStdout": False,
            "AttachStderr": False,
            "Tty": True,
            "OpenStdin": True,
            "StdinOnce": False,
            "Cmd": [
                "/bin/bash"
            ],
            "Image": "7a49ecc05fe4",
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
    try:
        return requests.post(rest_api + "/containers/create?name=" + name, data=json.dumps(payload), headers=headers)
    except requests.exceptions.RequestException as e:
        print("Error in getting a reply from the Docker REST API!\n\n"
            "Requests output:\n"
            + str(e))
        exit(1)
    
# function to create an excute command for an container using the docker API
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
    try: 
        r = requests.post(rest_api + "/containers/" + name + "/exec", data=json.dumps(payload), headers=headers)
    except requests.exceptions.RequestException as e:
        print("Error in getting a reply from the Docker REST API!\n\n"
            "Requests output:\n"
            + str(e))
        exit(1)
    try:
        assert r.status_code == 201
        data = json.loads(r.content.decode())
        return(data["Id"])
    except AssertionError:
        data = json.loads(r.content.decode())
        return("HTTP status code not correct!\n\n"
            "API output:\n"
            + r.text)

# function to create a new network using the docker API
def CreateNet(rest_api, net_name, parent_if, network="10.25.208.0", netmask="21"):
    payload = {
            "Name": net_name,
            "CheckDuplicate": True,
            "Driver": "macvlan",
            "EnableIPv6": False,
            "IPAM": {
                "Config": [{
                    "Subnet": network + "/" + netmask}]
                },
            "Options": {
                "parent": parent_if,
                "macvlan_mode": "vepa"
            }
        } 
    
    headers = {"content-type": "application/json"}
    try:
        r = requests.post(rest_api + "/networks/create", data=json.dumps(payload), headers=headers) 
    except requests.exceptions.RequestException as e:
        print("Error in getting a reply from the Docker REST API!\n\n"
            "Requests output:\n"
            + str(e))
        exit(1)
    try:
        assert r.status_code == 201
        data = json.loads(r.content.decode())
        return(data["Id"])
    except AssertionError:
        return("HTTP status code not correct!\n"
            "API output:"
            + r.text)

# function to retrieve container information from the docker API
def InspectContainer(rest_api, cont_name=""):
    try: 
        if cont_name == "":
            r = requests.get(rest_api + "/containers/json?all=1")
        else:
            r = requests.get(rest_api + "/containers/" + cont_name + "/json")
    except requests.exceptions.RequestException as e:
        print("Error in getting a reply from the REST API!\n\n"
            "Requests output:\n"
            + str(e))
        exit(1)
    try:
        assert r.status_code == 200
        return r.json()
    except AssertionError:
        return("HTTP status code not correct!\n\n"
            "API output:\n"
            + r.text)

# function to retreive network information from the docker API
def InspectNet(rest_api, net_name=""):
    try:
        if net_name == "":
            r = requests.get(rest_api + "/networks?filters={\"type\":{\"custom\":true}}")
        else:
            r = requests.get(rest_api + "/networks/" + net_name)
    except requests.exceptions.RequestException as e:
        print("Error in getting a reply from the Docker REST API!\n\n"
            "Requests output:\n"
            + str(e))
        exit(1)
    try:
        assert r.status_code == 200
        return r.json()
    except AssertionError:
        return("HTTP status code not correct!\n\n"
            "API output:\n"
            + r.text)

# function to kill and delete a container using the docker API
def RemoveContainer(rest_api, name):
    try:
        r = requests.delete(rest_api + "/containers/" + name)
    except requests.exceptions.RequestException as e:
        print("Error in getting a reply from the Docker REST API!\n\n"
            "Requests output:\n"
            + str(e))
        exit(1)
    try:
        assert r.status_code == 204
        return "Container " + name + " removed succesfully!"
    except AssertionError:
        return("HTTP status code not correct!\n\n"
            "API output:\n"
            + r.text)

# function to delete a network using the docker API
def RemoveNet(rest_api, name):
    try:
        r = requests.delete(rest_api + "/networks/" + name)
    except requests.exceptions.RequestException as e:
        print("Error in getting a reply from the Docker REST API!\n\n"
            "Requests output:\n"
            + str(e))
        exit(1)
    try:
        assert r.status_code == 204
        return "Network " + name + " removed succesfully!"
    except AssertionError:
        return("HTTP status code not correct!\n\n"
            "API output:\n"
            + r.text)

# function to start a container using the docker API
def StartContainer(rest_api, name):
    try:
        r = requests.post(rest_api + "/containers/" + name + "/start")
    except requests.exceptions.RequestException as e:
        print("Error in getting a reply from the Docker REST API!\n\n"
            "Requests output:\n"
            + str(e))
        exit(1)
    try:
        assert r.status_code == 204
        return "Container " + name + " started succesfully!"
    except AssertionError:
        return("HTTP status code not correct!\n\n"
            "API output:\n"
            + r.text)

# function to start an execute command in an container
def StartExec(rest_api, id, action):
    if action == "fg" :
        payload = {
                "Detach": False,
                "Tty": True
            }
    if action == "bg" :
        payload = {
                "Detach": True,
                "Tty": True
            }
    headers = {"content-type": "application/json"}
    try:
        r = requests.post(rest_api + "/exec/" + id + "/start", data=json.dumps(payload), headers=headers, stream=True)
    except requests.exceptions.RequestException as e:
        print("Error in getting a reply from the Docker REST API!\n\n"
            "Requests output:\n"
            + str(e))
        exit(1)
    try:
        assert r.status_code == 200
        return r
    except AssertionError:
        return("HTTP status code not correct!\n\n"
            "API output:\n"
            + r.text)

def StopContainer(rest_api, name):
    try:
        r = requests.post(rest_api + "/containers/" + name + "/stop")
    except requests.exceptions.RequestException as e:
        print("Error in getting a reply from the Docker REST API!\n\n"
            "Requests output:\n"
            + str(e))
        exit(1)
    try:
        assert r.status_code == 204
        return "Container " + name + " stopped succesfully!"
    except AssertionError:
        return("HTTP status code not correct!\n\n"
            "API output:\n"
            + r.text)
