import os
from scanner import Scan
from general import Connection
# from ipaddress import IPv4Network
from pprint import pp

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
ip = '10.3.0.1'
devicetype = 'cisco_ios'

connection = Connection(ip, username, password, devicetype)
pp(Scan(ip, '10.3.0.0/24', devicetype, '10', connection).all_hosts)
