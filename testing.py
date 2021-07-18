# import os
# from scanner import Scan
# from general import Connection
# # from progressbar import progressbar
# # from pprint import pp
#
# username = os.getenv('USERNAME')
# password = os.getenv('PASSWORD')
# mgmt_ip = '10.3.0.1'
# devicetype = 'cisco_ios'
#
# # networks = [
# #     '10.39.18.0/24', '10.39.20.0/24', '10.39.21.0/24', '10.39.22.0/24', '10.39.23.0/24', '10.39.1.0/24',
# #     '10.39.4.0/24', '192.168.253.0/24'
# # ]
# #
# # vlans = ['18', '20', '21', '22', '23', '192', '253', '2001', '2004']
# networks = [
#     '10.3.0.0/24'
# ]
#
# vlans = ['10']
#
# with open('netscan.csv', 'w+') as file:
#     length = len(networks) * len(vlans)
#     file.write('ip_address,mac_address,status,vlan\n')
#     # vlan_bar = progressbar(vlans, prefix='VLANS: ')
#     # for vlan in vlan_bar:
#     for vlan in vlans:
#         # network_bar = progressbar(networks, prefix='Networks: ')
#         # for network in network_bar:
#         for network in networks:
#             # n = network.split('.')
#             # intf_ip = f'{n[0]}.{n[1]}.{n[2]}.3'
#             connection = Connection(mgmt_ip, username, password, devicetype)
#             all_hosts = Scan(network, devicetype, vlan, connection, progress_bar=True).all_hosts
#             for host in all_hosts:
#                 address = host['address']
#                 try:
#                     mac = host['mac']
#                 except KeyError:
#                     mac = ''
#                 status = host['status']
#                 file.write(f'{address},{mac},{status},{vlan}\n')
from scanner import Scan
from general import Connection
import os

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
mgmt_ip = '10.3.0.1'
devicetype = 'cisco_ios'

networks = [
    '10.39.18.0/24', '10.39.20.0/24', '10.39.21.0/24', '10.39.22.0/24', '10.39.23.0/24', '10.39.1.0/24',
    '10.39.4.0/24', '192.168.253.0/24'
]

vlans = ['18', '20', '21', '22', '23', '192', '253', '2001', '2004']

with open('netscan.csv', 'w+') as file:
    length = len(networks) * len(vlans)
    file.write('ip_address,mac_address,status,vlan\n')
    for vlan in vlans:
        for network in networks:
            connection = Connection(mgmt_ip, username, password, devicetype)
            all_hosts = Scan(network, devicetype, vlan, connection, progress_bar=True).all_hosts
            for host in all_hosts:
                address = host['address']
                try:
                    mac = host['mac']
                except KeyError:
                    mac = ''
                status = host['status']
                file.write(f'{address},{mac},{status},{vlan}\n')
