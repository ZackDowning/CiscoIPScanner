import os
from scanner import Scan
from general import Connection
# from ipaddress import IPv4Network
# from pprint import pp

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
mgmt_ip = '10.39.16.2'
devicetype = 'cisco_ios'

networks = [
    '10.39.18.0/24', '10.39.20.0/24', '10.39.21.0/24', '10.39.22.0/24', '10.39.23.0/24', '10.39.1.0/24',
    '10.39.4.0/24', '192.168.253.0/24'
]

vlans = ['18', '20', '21', '22', '23', '192', '253', '2001', '2004']

for network in networks:
    n = network.split('.')
    intf_ip = f'{n[0]}.{n[1]}.{n[2]}.3'
    for vlan in vlans:
        connection = Connection(mgmt_ip, username, password, devicetype)
        all_hosts = Scan(network, devicetype, vlan, connection, True, intf_ip).all_hosts
