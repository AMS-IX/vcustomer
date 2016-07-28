# My AMS-IX REST API module
import json
import requests

# function to get the link JSON data
def GetLink(rest_api, link, value=""):
	r = requests.get(rest_api + "/api/v1/links/" + link)
	try:
		assert r.status_code == 200
		data = json.loads(r.content.decode())
	except AssertionError:
		return "HTTP status code not correct!"
		return ""
		return "API output:"
		return r.text
	# return all data
	if value == "":
		return(data)
	# return mac addresses data
	if value == "mac":
		try:
			return(data["mac_addresses"])[0]
		except IndexError:
			return "This link has no MAC address(es) assigned."
	# return physical ports data
	if value == "ports":
		try:
			return(data["ports"])[0]
		except IndexError:
			return "This link has no physical ports assigned."
	# return quarantine data
	if value == "quarantine":
		try:
			return(data["vlans"][0]["quarantine"])
		except IndexError:
			return "This link has no quarantine information assigned"
	# return vlan(s) data
	if value == "vlan":
		try:
			return(data["vlans"])[0]
		except IndexError:
			return "This link has no VLAN(s) assigned"
