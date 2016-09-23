# vcustomer.py - spinning up docker instances from the my-amsix api.

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
 
