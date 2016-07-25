# My AMS-IX REST API module
import json
import requests

# function to get the mac address(es) for a link
def GetMac(rest_api, link):
	r = requests.get(rest_api + "/api/v1/links/" + link)
	try:
		assert r.status_code == 200
		data = json.loads(r.content.decode())
		return(data["mac_addresses"])[0]
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text
	except IndexError:
		return "This link has no MAC address(es) assigned."

# function to get the physical port(s) for a link
def GetPort(rest_api, link):
	r = requests.get(rest_api + "/api/v1/links/" + link)
	try:
		assert r.status_code == 200
		data = json.loads(r.content.decode())
		return(data["ports"])[0]
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text
	except IndexError:
		return "This link has no physical port(s) assigned"

# function to get the vlan(s) for a link
def GetVlan(rest_api, link):
	r = requests.get(rest_api + "/api/v1/links/" + link)
	try:
		assert r.status_code == 200
		data = json.loads(r.content.decode())
		return(data["vlans"])[0]
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text
	except IndexError:
		return "This link has no VLAN(s) assigned"	
