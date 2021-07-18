# CiscoIPScanner
IPv4 subnet scanner for MAC addresses and reachability from Cisco IOS(-XE) and NX-OS devices.  
  
General use case is for IP scanning of remote networks without remote connectivity to a device within that network or scanning for multiple networks within one or more VLANs.  
## Requirements
- Python3.9 *(May work with other versions; only tested with 3.9)*
- Packages:
  - netmiko
  - progressbar2
  - icmplib
- CiscoIPScanner package within Python 'site-packages' directory
- Cisco L3 switch running IOS, IOS-XE, or NX-OS *(Adding router support later)*
- Up to 11 available VTY lines on switch all configured for either SSH or TELNET
- Credentials with privledged (level 15) access to said switch unless new SVI is not necessary for scan *(See more details below)* Otherwise just credentials for read access
- Inputs values:
  - Network in CIDR format (e.g. 10.0.0.0/24) within /23 through /29 prefix lengths
  - VLAN ID compliant with Cisco VLAN ID range to run IP scan within
  - IP address not in use within network to scan if device does not already have SVI
  - NX-OS: If device has existing SVI in desired source VLAN, IP address of existing SVI
## Example Syntax
Scan for single network and single VLAN with progress bar for each scan segment outputting results to CSV file
```
from CiscoIPScanner import Scan, Connection
import os

username = os.getenv('USERNAME')
password = os.getenv('PASSWORD')
mgmt_ip = '10.3.0.1'
devicetype = 'cisco_ios'
network = '10.39.18.0/24'
vlan = '18'

with open('netscan.csv', 'w+') as file:
    # Creates SSH session
    connection = Connection(mgmt_ip, username, password, devicetype)
    # Calls Scan class to initiate scan and attribute all_hosts containing list of dictionaries for each
    # host in network ID
    all_hosts = Scan(network, devicetype, vlan, connection, progress_bar=True).all_hosts
    for host in all_hosts:
        address = host['address']
        try:
            mac = host['mac']
        except KeyError:
            mac = ''
        status = host['status']
        file.write(f'{address},{mac},{status},{vlan}\n')
```
  
Scan for multiple networks within multiple VLANs with progress bar for each scan segment outputting results to CSV file
```
from CiscoIPScanner import Scan, Connection
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
    file.write('ip_address,mac_address,status,vlan\n')
    for vlan in vlans:
        for network in networks:
            ip = network.split('.')
            # Available IP address not in use for subnet to scan
            intf_ip = f'{ip[0]}.{ip[1]}.{ip[2]}.3'
            # Creates SSH session
            connection = Connection(mgmt_ip, username, password, devicetype)
            # Calls Scan class to initiate scan and attribute all_hosts containing list of dictionaries for each
            # host in network ID
            # 'True' here is to initiate creation of new SVI
            all_hosts = Scan(network, devicetype, vlan, connection, True, progress_bar=True).all_hosts
            for host in all_hosts:
                address = host['address']
                try:
                    mac = host['mac']
                except KeyError:
                    mac = ''
                status = host['status']
                file.write(f'{address},{mac},{status},{vlan}\n')
```
## WARNING
I ***do not*** recommend running this on low-end devices to prevent unexpected resource utilization issues.  General rule of thumb would be not to run on anything EOL
