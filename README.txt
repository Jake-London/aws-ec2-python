Jake London
0961071
4010 - A2

What does launch.py do:
 - As is in the repo, launch.py will create the required Amazon Linux 2 and Ubuntu 20.04 instances, transfer a index.html,
   shell script (createServer.sh), and Dockerfile in order to setup a static nginx html site accessible through the instance
   public ip address
 - IMPORTANT The server is accessible at port 80 only, so to visit simply type: "http://xx.xx.xx.xx". Do not specify another port.
 - To show that additional instances can be created, a Red Hat template is used to create a default redhat instance.
 - Nothing is done with the instance (no docker install, no updates, etc.). It is simply their to show that additional templates/instances can be added

How to run launch.py:
- Ensure template.csv, container.csv, instances.csv are in the same folder as launch.py
- container.csv must have containers defined in it if they appear in the instances.csv
- template and instances must have at least one entry each
- If an instance has no package, then "none" is used in place of a package name
- SSH private key files must be in same folder as launch.py AND specified in instances.csv
- createServer.sh must be in the launch.py directory along with Dockerfile in order to setup nginx server
- index.html file to be used on nginx server must be in launch.py folder
- no command line arguments required

To Run:
	python launch.py
	OR
	python3 launch.py
	(depending on system setup)

====================================================================================================================================

What does monitor.py do:
 - Prints information about ec2 instances: name, id, launch date, status

How to run monitor.py:
 - No command line arguments required

To Run:
	python monitor.py
	OR
	python3 monitor.py
	(depending on system setup)