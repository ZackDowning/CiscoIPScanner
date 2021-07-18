from ipaddress import IPv4Network, AddressValueError
from CiscoIPScanner.general import mt
from CiscoIPScanner.exceptions import (
    InvalidVRF, NoVRFSpecifiedWithIntInVRF, InvalidIntfIPAddress, InvalidDeviceType, NoIntfIPSpecified,
    NoNXOSIntfIPSpecified, SubnetTooLarge, InvalidVlanID, InvalidNetworkID, InvalidInterfaceIP,
    InterfaceIPAddressNotInNetwork, VlanNotInVlanDB, TemplatesNotFoundWithinPackage)
from CiscoIPScanner.address_validator import ipv4
from progressbar import progressbar
# import time

# TODO: Add router support
# TODO: Add check to make sure SVI


def hosts_lists_parse(prefix, all_hosts):
    """Splits host list into seperate lists for concurrent SSH or TELNET sessions for faster IP scan\n
    if prefix length is between 29 and 23"""
    if prefix == 29:
        return [
            all_hosts[0:2], all_hosts[2:4], all_hosts[4:6]
        ]
    elif prefix == 28:
        return [
            all_hosts[0:2], all_hosts[2:4], all_hosts[4:6], all_hosts[6:8],
            all_hosts[8:10], all_hosts[10:12], all_hosts[12:14]
        ]
    elif prefix == 27:
        return [
            all_hosts[0:5], all_hosts[5:10], all_hosts[10:15], all_hosts[15:20],
            all_hosts[20:25], all_hosts[25:30]
        ]
    elif prefix == 26:
        return [
            all_hosts[0:15], all_hosts[15:30], all_hosts[30:45], all_hosts[45:60],
            all_hosts[60:62]
        ]
    elif prefix == 25:
        return [
            all_hosts[0:18], all_hosts[18:36], all_hosts[36:54], all_hosts[54:72],
            all_hosts[72:90], all_hosts[89:108], all_hosts[108:126]
        ]
    elif prefix == 24:
        return [
            all_hosts[0:25], all_hosts[25:50], all_hosts[50:75], all_hosts[75:100],
            all_hosts[100:125], all_hosts[125:150], all_hosts[150:175], all_hosts[175:200],
            all_hosts[200:225], all_hosts[225:250], all_hosts[250:254]
        ]
    elif prefix == 23:
        return [
            all_hosts[0:51], all_hosts[51:102], all_hosts[102:153], all_hosts[153:204],
            all_hosts[204:255], all_hosts[255:306], all_hosts[306:357], all_hosts[357:408],
            all_hosts[408:459], all_hosts[459:510]
        ]
    else:
        raise SubnetTooLarge


class ProgressBar:
    def __init__(self, iterable, prefix):
        self.bar = progressbar(iterable, prefix=prefix)


class Scan:
    """Initiates IP scan of IP subnet from Cisco IOS or NX-OS devices\n
    Subnet can be between a /29 and /23"""
    def __init__(self, network, devicetype, source_vlan, connection, create_intf=False, intf_ip=None, vrf=None,
                 count=2, timeout=1, progress_bar=False):

        # Intf IP required if creating interface
        if create_intf and intf_ip is None:
            raise NoIntfIPSpecified

        # Intf IP required if NX-OS
        if devicetype == 'cisco_nxos' and intf_ip is None:
            raise NoNXOSIntfIPSpecified

        # Checks VLAN to make sure valid VLAN ID within extended VLAN range and not within reserved VLAN ID range
        if int(source_vlan) not in range(1, 4095) or int(source_vlan) in range(1002, 1006):
            raise InvalidVlanID

        # Checks to make sure network is valid
        try:
            network = IPv4Network(network)
        except AddressValueError:
            raise InvalidNetworkID

        # Checks to make sure interface IP address is valid IP address and IP address in within the specific network
        if intf_ip is not None:
            if not ipv4(intf_ip):
                raise InvalidInterfaceIP
            if not any(intf_ip == str(h1) for h1 in network.hosts()):
                raise InterfaceIPAddressNotInNetwork
        
        # Checks for source vlan in device VLAN database
        session = connection.connection().session
        try:
            vlan_db = session.send_command('show vlan brief', use_textfsm=True)
        except ValueError:
            raise TemplatesNotFoundWithinPackage
        if not any(source_vlan == v1['vlan_id'] for v1 in vlan_db):
            raise VlanNotInVlanDB

        # Creates Interface
        if create_intf and intf_ip is not None:
            if vrf is None:
                session.send_config_set([
                    f'interface vlan {source_vlan}',
                    f'ip address {intf_ip} {network.netmask}',
                    'no shut'
                ])
            else:
                if devicetype == 'cisco_nxos':
                    vrf_cmd = f'vrf member {vrf}'
                else:
                    vrf_cmd = f'vrf forwarding {vrf}'
                session.send_config_set([
                    f'interface vlan {source_vlan}',
                    vrf_cmd,
                    f'ip address {intf_ip} {network.netmask}',
                    'no shut'
                ])
                
        # Creating list of dictionaries for hosts for later sorted of unordered output data from scan
        self.all_hosts = []
        """All hosts in specified subnet with dictionaries including reachability info, ip address, and mac address"""
        for h in network.hosts():
            self.all_hosts.append(
                {
                    'address': str(h)
                }
            )

        reachable_devices = []

        def scan(host, conn):
            """Main IP subnet Scan function"""
            ip_address = host['address']
            # Formats input command for proper formatting based on if IOS(-XE) or NX-OS operating system
            # Also checks to make sure device type is IOS(-XE) or NX-OS
            if devicetype == 'cisco_ios':
                if vrf is None:
                    cmd = f'ping {ip_address} repeat {count} timeout {timeout} source vlan {source_vlan}'
                else:
                    cmd = f'ping vrf {vrf} {ip_address} repeat {count} timeout {timeout} source vlan {source_vlan}'
            elif devicetype == 'cisco_nxos':
                if vrf is None:
                    cmd = f'ping {ip_address} count {count} timeout {timeout} source {intf_ip}'
                else:
                    cmd = f'ping {ip_address} vrf {vrf} count {count} timeout {timeout} source {intf_ip}'
            else:
                raise InvalidDeviceType

            cmd_output = conn.send_command(cmd)
            
            # Checks for cmd input errors
            if cmd_output.__contains__('Invalid'):
                if devicetype == 'cisco_ios':
                    if cmd_output.__contains__(
                            'Invalid source interface - Interface vrf does not match the vrf used for ping'):
                        raise NoVRFSpecifiedWithIntInVRF
                    if cmd_output.__contains__('does not exist'):
                        raise InvalidVRF
                    if cmd_output.__contains__('input detected'):
                        raise InvalidIntfIPAddress
                else:
                    if cmd_output.__contains__('bind to address'):
                        raise NoVRFSpecifiedWithIntInVRF
                    if cmd_output.__contains__('does not exist'):
                        raise InvalidVRF
                    if cmd_output.__contains__('Invalid host/interface'):
                        raise InvalidIntfIPAddress
            else:
                # Checks if device recieved ping echo then appending IP address to list if non-0 value
                if devicetype == 'cisco_ios':
                    try:
                        if str(cmd_output.split('\n')[4].split(' ')[3]) != '0':
                            reachable_devices.append(ip_address)
                    except IndexError:
                        if str(cmd_output.split('\n')[5].split(' ')[3]) != '0':
                            reachable_devices.append(ip_address)
                else:
                    if str(cmd_output.split('\n')[5].split(' ')[3]) != '0':
                        reachable_devices.append(ip_address)

        # Splits hosts list into mulitple smaller lists for for multiple asyncronous SSH/TELNET sessions
        hosts_lists = hosts_lists_parse(int(network.prefixlen), self.all_hosts)

        if progress_bar:
            self.phase_num = 1
            """Internal use only for progress bar numbers"""

        def host_split(host_list):
            session1 = connection.connection().session
            if progress_bar:
                bar = ProgressBar(host_list, f'Phase {str(self.phase_num)}: ').bar
                self.phase_num += 1
                for h1 in bar:
                    scan(h1, session1)
            else:
                for h1 in host_list:
                    scan(h1, session1)
            session1.disconnect()
        
        mt(host_split, hosts_lists, threads=len(hosts_lists))

        arps = session.send_command(f'show ip arp vlan {source_vlan}', use_textfsm=True)

        # Creates Interface
        if create_intf:
            session.send_config_set([f'no interface vlan {source_vlan}'])
        session.disconnect()

        def sort(host):
            for arp in arps:
                if arp['address'] == host['address'] and arp['mac'].count('.') == 2:
                    host['mac'] = arp['mac']
            if any(host['address'] == reachable_device for reachable_device in reachable_devices):
                host['status'] = 'Reachable'
            else:
                host['status'] = 'Unreachable'

        mt(sort, self.all_hosts)
