from ipaddress import IPv4Network
from general import mt
import exceptions as e
import time

# TODO: Clean up scan
# TODO: Add check to see if interface already exists on ios and nxos for source vlan
# TODO: Check to make sure vlan exists in vlan db
# TODO: break down Scan class
# TODO: Add check to make sure provided intf ip address is within subnet to scan for


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
            raise e.NoIntfIPSpecified

        # Intf IP required if NXOS
        if devicetype == 'cisco_nxos' and intf_ip is None:
            raise e.NoNXOSIntfIPSpecified

        network = IPv4Network(network)

        # Creates Interface
        if create_intf and intf_ip is not None:
            if vrf is None:
                self.session.send_config_set([
                    f'interface vlan {source_vlan}',
                    f'ip address {intf_ip} {network.netmask}',
                    'no shut',
                    'do wr'
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
                    'do wr'
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
                raise e.InvalidDeviceType
            cmd_output = conn.send_command(cmd)
            # return cmd_output
            if cmd_output.__contains__('Invalid'):
                if self.devicetype == 'cisco_ios':
                    if cmd_output.__contains__(
                            'Invalid source interface - Interface vrf does not match the vrf used for ping'):
                        raise e.NoVRFSpecifiedWithIntInVRF
                    if cmd_output.__contains__('does not exist'):
                        raise e.InvalidVRF
                    if cmd_output.__contains__('input detected'):
                        raise e.InvalidIntf
                else:
                    if cmd_output.__contains__('bind to address'):
                        raise e.NoVRFSpecifiedWithIntInVRF
                    if cmd_output.__contains__('does not exist'):
                        raise e.InvalidVRF
                    if cmd_output.__contains__('Invalid host/interface'):
                        raise e.InvalidIntf
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
                self.all_hosts[0:2], self.all_hosts[2:4], self.all_hosts[4:6]
            ]
        elif prefix == 28:
            hosts_lists = [
                self.all_hosts[0:2], self.all_hosts[2:4], self.all_hosts[4:6], self.all_hosts[6:8],
                self.all_hosts[8:10], self.all_hosts[10:12], self.all_hosts[12:14]
            ]
        elif prefix == 27:
            hosts_lists = [
                self.all_hosts[0:5], self.all_hosts[5:10], self.all_hosts[10:15], self.all_hosts[15:20],
                self.all_hosts[20:25], self.all_hosts[25:30]
            ]
        elif prefix == 26:
            hosts_lists = [
                self.all_hosts[0:15], self.all_hosts[15:30], self.all_hosts[30:45], self.all_hosts[45:60],
                self.all_hosts[60:62]
            ]
        elif prefix == 25:
            hosts_lists = [
                self.all_hosts[0:18], self.all_hosts[18:36], self.all_hosts[19:54], self.all_hosts[54:72],
                self.all_hosts[72:90], self.all_hosts[89:108], self.all_hosts[108:126]
            ]
        elif prefix == 24:
            hosts_lists = [
                self.all_hosts[0:25], self.all_hosts[25:50], self.all_hosts[50:75], self.all_hosts[75:100],
                self.all_hosts[100:104], self.all_hosts[125:149], self.all_hosts[150:174], self.all_hosts[175:199],
                self.all_hosts[200:224], self.all_hosts[225:249], self.all_hosts[250:253]
            ]
        elif prefix == 23:
            hosts_lists = [
                self.all_hosts[0:51], self.all_hosts[51:102], self.all_hosts[102:153], self.all_hosts[103:204],
                self.all_hosts[204:255], self.all_hosts[255:306], self.all_hosts[306:357], self.all_hosts[357:408],
                self.all_hosts[408:459], self.all_hosts[459:510]
            ]
        else:
            raise e.SubnetTooLarge

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

        # Creates Interface
        if create_intf and intf_ip is not None:
            session.send_config_set([f'no interface vlan {source_vlan}', 'do wr'])

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
