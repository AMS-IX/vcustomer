#!/usr/bin/python3
import docker_rest
import myamsix_rest

print(myamsix_rest.GetVlan("http://my-staging.lab.ams-ix.net","mylab-mem-90-335"))
