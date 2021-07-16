# import os
# from scanner import Scan
# from general import Connection
# from ipaddress import IPv4Network
# from pprint import pp
#
# username = os.getenv('USERNAME')
# password = os.getenv('PASSWORD')
# ip = '10.39.16.2'
# devicetype = 'cisco_ios'
#
# networks = [
#     '10.39.18.0/24', '10.39.20.0/24', '10.39.21.0/24', '10.39.22.0/24', '10.39.23.0/24', '10.39.1.0/24',
#     '10.39.4.0/24', '192.168.253.0/24'
# ]
#
# vlans = ['18', '20', '21', '22', '23', '192', '253', '2001', '2004']

network = '10.39.18.0/24'
ip_address = f'{network.split(".")[1:3]}.3'
print(ip_address)
# for network in networks:
#     ip_address = f'{network.split(".")[0:2]}.3'
#     for vlan in vlans:
#
