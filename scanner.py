from ipaddress import IPv4Network
from general import mt
import time

# TODO: Clean up scan
# TODO: Add check to see if interface already exists on ios and nxos for source vlan
# TODO: Check to make sure vlan exists in vlan db
# TODO: break down Scan class
# TODO: move exceptions to seperate file


class InvalidVRF(Exception):
    pass


class NoVRFSpecifiedWithIntInVRF(Exception):
    pass


class InvalidIntf(Exception):
    pass


class InvalidDeviceType(Exception):
    pass


class NoIntfIPSpecified(Exception):
    pass


class NoNXOSIntfIPSpecified(Exception):
    pass


class SubnetTooLarge(Exception):
    pass


class Scan:
    def __init__(self, management_ip_address, network, devicetype, source_vlan, connection, create_intf=False,
                 intf_ip=None, vrf=None, count=2, timeout=1):
        self.session = connection.connection().session
        self.management_ip_address = management_ip_address
        self.network = network
        self.devicetype = devicetype
        self.reachable_devices = []
        self.devices = []
        self.all_hosts = []

        # Intf IP required if creating interface
        if create_intf and intf_ip is None:
            raise NoIntfIPSpecified

        # Intf IP required if NXOS
        if devicetype == 'cisco_nxos' and intf_ip is None:
            raise NoNXOSIntfIPSpecified

        network = IPv4Network(network)

        # Creates Interface
        if create_intf and intf_ip is not None:
            if vrf is None:
                self.session.send_config_set([
                    f'interface vlan {source_vlan}',
                    f'ip address {intf_ip} {network.netmask}',
                    'no shut',
                    'copy run start'
                ])
            else:
                if devicetype == 'cisco_nxos':
                    vrf_cmd = f'vrf member {vrf}'
                else:
                    vrf_cmd = f'vrf forwarding {vrf}'
                self.session.send_config_set([
                    f'interface vlan {source_vlan}',
                    vrf_cmd,
                    f'ip address {intf_ip} {network.netmask}',
                    'no shut',
                    'copy run start'
                ])

        hosts_r = network.hosts()
        for h in hosts_r:
            self.all_hosts.append(
                {
                    'address': str(h)
                }
            )

        def scan(host, conn):
            ip_address = host['address']
            print(ip_address)
            # TODO: Add interface format checking
            if self.devicetype == 'cisco_ios':
                if vrf is None:
                    cmd = f'ping {ip_address} repeat {count} timeout {timeout} source vl{source_vlan}'
                else:
                    cmd = f'ping vrf {vrf} {ip_address} repeat {count} timeout {timeout} source vl{source_vlan}'
            elif self.devicetype == 'cisco_nxos':
                if vrf is None:
                    cmd = f'ping {ip_address} count {count} timeout {timeout} source {intf_ip}'
                else:
                    cmd = f'ping {ip_address} vrf {vrf} count {count} timeout {timeout} source {intf_ip}'
            else:
                raise InvalidDeviceType
            cmd_output = conn.send_command(cmd)
            # return cmd_output
            if cmd_output.__contains__('Invalid'):
                if self.devicetype == 'cisco_ios':
                    if cmd_output.__contains__(
                            'Invalid source interface - Interface vrf does not match the vrf used for ping'):
                        raise NoVRFSpecifiedWithIntInVRF
                    if cmd_output.__contains__('does not exist'):
                        raise InvalidVRF
                    if cmd_output.__contains__('input detected'):
                        raise InvalidIntf
                else:
                    if cmd_output.__contains__('bind to address'):
                        raise NoVRFSpecifiedWithIntInVRF
                    if cmd_output.__contains__('does not exist'):
                        raise InvalidVRF
                    if cmd_output.__contains__('Invalid host/interface'):
                        raise InvalidIntf
            else:
                if self.devicetype == 'cisco_ios':
                    try:
                        if str(cmd_output.split('\n')[4].split(' ')[3]) != '0':
                            self.reachable_devices.append(ip_address)
                    except IndexError:
                        if str(cmd_output.split('\n')[5].split(' ')[3]) != '0':
                            self.reachable_devices.append(ip_address)
                else:
                    if str(cmd_output.split('\n')[5].split(' ')[3]) != '0':
                        self.reachable_devices.append(ip_address)

        prefix = int(network.prefixlen)
        if prefix == 29:
            hosts_lists = [
                self.all_hosts[0:1], self.all_hosts[2:3], self.all_hosts[4:5]
            ]
        elif prefix == 28:
            hosts_lists = [
                self.all_hosts[0:1], self.all_hosts[2:3], self.all_hosts[4:5], self.all_hosts[6:7],
                self.all_hosts[8:9], self.all_hosts[10:11], self.all_hosts[12:13]
            ]
        elif prefix == 27:
            hosts_lists = [
                self.all_hosts[0:4], self.all_hosts[5:9], self.all_hosts[10:14], self.all_hosts[15:19],
                self.all_hosts[20:24], self.all_hosts[25:29]
            ]
        elif prefix == 26:
            hosts_lists = [
                self.all_hosts[0:14], self.all_hosts[15:29], self.all_hosts[30:44], self.all_hosts[45:59],
                self.all_hosts[60:61]
            ]
        elif prefix == 25:
            hosts_lists = [
                self.all_hosts[0:17], self.all_hosts[18:35], self.all_hosts[19:53], self.all_hosts[54:71],
                self.all_hosts[72:89], self.all_hosts[89:107], self.all_hosts[108:125]
            ]
        elif prefix == 24:
            hosts_lists = [
                self.all_hosts[0:24], self.all_hosts[25:49], self.all_hosts[50:74], self.all_hosts[75:99],
                self.all_hosts[100:104], self.all_hosts[125:149], self.all_hosts[150:174], self.all_hosts[175:199],
                self.all_hosts[200:224], self.all_hosts[225:249], self.all_hosts[250:253]
            ]
        elif prefix == 23:
            hosts_lists = [
                self.all_hosts[0:50], self.all_hosts[51:101], self.all_hosts[102:152], self.all_hosts[103:203],
                self.all_hosts[204:254], self.all_hosts[255:305], self.all_hosts[306:356], self.all_hosts[357:407],
                self.all_hosts[408:458], self.all_hosts[459:509]
            ]
        else:
            raise SubnetTooLarge

        def host_split(host_list):
            session1 = connection.connection().session
            for h1 in host_list:
                time.sleep(1)
                scan(h1, session1)
            session1.disconnect()

        start = time.perf_counter()
        mt(host_split, hosts_lists, threads=len(hosts_lists))
        end = time.perf_counter()
        print(f'finished in {round(end - start, 0)} seconds')

        session = connection.connection().session
        arps = session.send_command(f'show ip arp vlan {source_vlan}', use_textfsm=True)
        session.disconnect()

        def append(arp):
            if arp['mac'].count('.') == 2:
                self.devices.append(
                    {
                        'address': arp['address'],
                        'mac': arp['mac']
                    }
                )

        mt(append, arps)

        def sort(host):
            for device in self.devices:
                if device['address'] == host['address']:
                    host['mac'] = device['mac']
            if any(
                    reachable_device for reachable_device in self.reachable_devices
                    if host['address'] == reachable_device
            ):
                host['Status'] = 'Reachable'
            else:
                host['Status'] = 'Unreachable'

        mt(sort, self.all_hosts)
