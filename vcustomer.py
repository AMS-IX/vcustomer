#!/usr/bin/python3
"""vcustomer.py - spinning up docker instances from the my-amsix api.

Usage:
    vcustomer.py --create (quarantine|isp|partner) <docker_api> <link-id> <docker_net>
    vcustomer.py --convert (quarantine|isp|partner) <docker_api> <link-id>
    vcustomer.py --execute (foreground|background) <docker_api> <link-id> <command>
    vcustomer.py --init-net <docker_api> <docker_net> <docker_phys> <link-id>
    vcustomer.py --list <docker_api>
    vcustomer.py --list-net <docker_api>
    vcustomer.py --remove <docker_api> <link-id>
    vcustomer.py --remove-net <docker_api> <docker_net>
    vcustomer.py --wipe <docker_api>

Options:
    -h --help   Show this screen.
    --version   Show version.

Author: Joris Claassen

"""
import hashlib
import json
from docopt import docopt
from netaddr import IPNetwork
import docker_rest
import myamsix_rest

args = docopt(__doc__, version='vcustomer.py 0.0.1')

def AddAddress(svlan, ip="", subnet=""):
    Execute("ip link add link eth0 eth0." + svlan + " type vlan proto 802.1ad id " + svlan)
    Execute("ip link set eth0." + svlan + " up")
    if ip != "" and subnet != "":
        Execute("ip addr add " + ip + "/" + subnet + " dev eth0." + svlan)

def AddRoute(network, subnet, vlan):
    Execute("ip route add " + network + "/" + subnet + " via dev eth0." + vlan)

def Create():
    link = myamsix_rest.GetLink(myamsix_api, args["<link-id>"])
    try:
        addr = link["vlans"][0]["routers"][0]["quarantine"]["address"]
        subnet = link["vlans"][0]["routers"][0]["quarantine"]["netmask"]
    except IndexError:
        try:
            addr = link["quarantined_ipv4_address"]
        except KeyError:
            # partners do not have a quarantine IP after enabling
            if args["partner"]:
                addr = "10.25.7.1" 
            else:
                print("Failed to get any quarantine address for this link-id, does it exist, or is the link already enabled?")
                exit(1)
            subnet = 21
    ip = IPNetwork(str(addr) + "/" + str(subnet))
    create = docker_rest.CreateContainer(args["<docker_api>"], args["<link-id>"],
                                         args["<docker_net>"], str(ip.ip))
    data = json.loads(create.content.decode())
    try:
        assert create.status_code == 201
        print("Container created succesfully!")
        print(docker_rest.StartContainer(args["<docker_api>"], data["Id"]))
    except AssertionError:
        print("Container not created succesfully:\n\n" +
              data["message"])
        exit(1)
    if args["quarantine"]:
        ConvertTo("quarantine")
    elif args["isp"]:
        ConvertTo("isp")
    elif args["partner"]:
        ConvertTo("partner")

def CreateVlan(linkid):
    linkhash = hashlib.sha256(linkid.encode()).hexdigest()
    if int(linkhash, 16)%10000 < 4090:
        vlan = int(linkhash, 16)%10000
        return vlan
    else:
        vlan = int(linkhash, 16)%1000
        return vlan

def ConvertTo(target):
    link = myamsix_rest.GetLink(myamsix_api, args["<link-id>"])
    # generate service vlan based on link-id
    vlan = CreateVlan(args["<link-id>"])
    # clear all existing network config in the container
    FlushAddress(vlan)
    # extract production ipv4 ip if isp vlan is requested
    if target == "isp":
        if "virtual_links" in link:
            print("This is a partner (reseller) port, are you sure the port belongs in isp vlan?")
        try:
            for router in link["vlans"][0]["routers"]:
                if router["class"].startswith("Ipv4"):
                    addr = router["ip"]
                    subnet = router["netmask"]
        except:
            print("Failed to convert to ISP: No vlans in this link-id")
            exit(1)
    # extract quarantine ipv4 ip if isp vlan is requested
    elif target == "quarantine":
        try:
            addr = link["vlans"][0]["routers"][0]["quarantine"]["address"]
            subnet = link["vlans"][0]["routers"][0]["quarantine"]["netmask"]
        except:
            try:
                addr = link["quarantined_ipv4_address"]
            except KeyError:
                print("Failed to get any quarantine address for this link-id, does it exist?")
                exit(1)
            subnet = 21
    if target == "quarantine" or target == "isp":
        ip = IPNetwork(str(addr) + "/" + str(subnet))
        # add address and route to the container
        AddAddress(str(vlan), str(ip.ip), str(ip.prefixlen))
        AddRoute(str(vlan), str(ip.network), str(ip.prefixlen))
    # check if link is a reseller link
    elif target == "partner":
        AddAddress(str(vlan))
    print("Container " + args["<link-id>"] + " succesfully converted to " + target +
          " vlan, service vlan " + str(vlan) + ".")
    # print the attached physical network adapter and physical port (pxc or edge)
    global if_tagged
    for interface in docker_rest.InspectContainer(args["<docker_api>"],args["<link-id>"])["NetworkSettings"]["Networks"]:
        if_tagged=interface
        print("This container is physically connected to " + interface)
    global if_untagged
    for port in link["ports"]:
        print("The port this container should be connected to is " + port["formatted"])
        if_untagged=port["formatted"]
    print()
    # print m6_provision command - this should be automatically called later!
    print("m6_provision --add-qinq-bridge " + if_tagged + " " + if_untagged + " " + str(vlan))

def Execute(command=args["<command>"]):
    global action
    action = "bg"
    if args["foreground"]:
        action = "fg"
    cmd = docker_rest.StartExec(args["<docker_api>"], docker_rest.CreateExec(args["<docker_api>"],
                                                                             args["<link-id>"],
                                                                             command), action)
    try:
        assert cmd.status_code == 200
        if action == "bg":
            return(cmd.text)
        if action == "fg":
            print(cmd.text)
    except (AssertionError, AttributeError):
        print("Pushing execute command to container failed, does it exist?")
        exit(1)

def FlushAddress(vlan):
    Execute("ip addr flush dev eth0")
    Execute("ip addr flush dev eth0." + str(vlan))

def InitNet():
    link = myamsix_rest.GetLink(myamsix_api, args["<link-id>"])
    addr = link["vlans"][0]["routers"][0]["quarantine"]["address"]
    subnet = 16
    ip = IPNetwork(str(addr) + "/" + str(subnet))
    # initiate a netork based on the /16 quarantine address of the supplied link-id
    print(docker_rest.InspectNet(args["<docker_api>"], docker_rest.CreateNet(args["<docker_api>"],
                                                                             args["<docker_net>"],
                                                                             args["<docker_phys>"],
                                                                             str(ip.network),
                                                                             str(ip.prefixlen))))

def Remove():
    # generate service vlan based on link-id
    vlan = CreateVlan(args["<link-id>"])
    # stop container
    print(docker_rest.StopContainer(args["<docker_api>"], args["<link-id>"]))
    # remove container
    print(docker_rest.RemoveContainer(args["<docker_api>"], args["<link-id>"]))
    # print m6_provision command - this should be automatically called later!
    print("m6_provision --del-qinq-bridge " + str(vlan))


#myamsix_api = "http://my.ams-ix.net"
myamsix_api = "http://my-staging.lab.ams-ix.net"

# create and start docker container based on myamsix link id
if args["--create"]:
    Create()

# convert ip settings to isp or quarantine
if args["--convert"]:
    if args["isp"]:
        ConvertTo("isp")
    if args["quarantine"]:
        ConvertTo("quarantine")
    if args["partner"]:
        ConvertTo("partner")

# execute command in container
if args["--execute"]:
    Execute()

# initialize docker network based on the ip and subnet received from the myamsix api
if args["--init-net"]:
    InitNet()

# list all running containers on this server
if args["--list"]:
    containers = docker_rest.InspectContainer(args["<docker_api>"])
    for vcustomer in containers:
        print(str(vcustomer["Names"][0])[1:])

# list all networks that the docker host has defined
if args["--list-net"]:
    networks = docker_rest.InspectNet(args["<docker_api>"])
    try:
        for network in networks:
            print(str(network["Name"]))
    except TypeError:
        print("There are no docker networks defined on this host")

# stop and remove docker container
if args["--remove"]:
   Remove() 

# remove docker network
if args["--remove-net"]:
    print(docker_rest.RemoveNet(args["<docker_api>"], args["<docker_net>"]))

# wipe all containers and networks
if args["--wipe"]:
    containers = docker_rest.InspectContainer(args["<docker_api>"])
    for vcustomer in containers:
        print(docker_rest.StopContainer(args["<docker_api>"], (str(vcustomer["Names"][0])[1:])))
        print(docker_rest.RemoveContainer(args["<docker_api>"], (str(vcustomer["Names"][0])[1:])))
    networks = docker_rest.InspectNet(args["<docker_api>"])
    try:
        for network in networks:
            print(docker_rest.RemoveNet(args["<docker_api>"], str(network["Name"])))
    except TypeError:
        print("There are no docker containers and or networks defined on this host")
