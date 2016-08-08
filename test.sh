#!/bin/bash
python3 request.py create network macvlan1 eth1
python3 request.py inspect network macvlan1
python3 request.py create container macvlan1 macvlan1 10.25.208.10 12:34:56:78:9a:bc
python3 request.py inspect container macvlan1
python3 request.py start container macvlan1
python3 request.py delete container macvlan1 
python3 request.py delete network macvlan1
