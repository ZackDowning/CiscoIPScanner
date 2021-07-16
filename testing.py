import os
from scanner import Scan
from general import Connection
# from ipaddress import IPv4Network
from pprint import pp

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
ip = '10.39.16.2'
devicetype = 'cisco_ios'

networks = [

]

connection = Connection(ip, username, password, devicetype)
pp(Scan(ip, '192.168.253.0/24', devicetype, '22', connection, True, '192.168.253.3').all_hosts)

