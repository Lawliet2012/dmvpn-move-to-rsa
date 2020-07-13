from pyats import aetest
from pprint import pprint
import re

class CommonSetup(aetest.CommonSetup):
    
    @aetest.subsection
    def connect_to_devices(self, testbed, steps):
        for device in testbed.devices:
            with steps.start('Connecting to %s' % device):
                testbed.devices[device].connect()
        

# define common cleanup after all tests are finished
class CommonCleanup(aetest.CommonCleanup):
    
    @aetest.subsection
    def disconnect_from_devices(self, testbed, steps):
        for dev_name, device in testbed.devices. items():
            with steps.start('Disconnecting from %s' % dev_name):
                device.disconnect()

class dmvpn_ping(aetest.Testcase):
    import os
    import json
    localip = {}

    @aetest.test
    def gathering_ip(self, testbed, steps):
        for dev_name, device in testbed.devices.items():
            self.localip[device.hostname] = []
            if device.hostname !="hub":
                with steps.start('Gathering ip with 10/8 from %s' % dev_name):
                    inside_interfaces = device.parse('show ip interface')
                    for intf in inside_interfaces.values():
                        ipaddr = intf.get('ipv4')
                        if ipaddr is not None:
                            for ipv4 in ipaddr.values():
                                if re.match(r'^172\.16.*$',ipv4['ip']):
                                    self.localip[device.hostname].append(ipv4['ip'])
                            pprint(self.localip[device.hostname].get())
                            if not self.localip[device.hostname]:
                                for ipv4 in ipaddr.values():
                                    if re.match(r'^10\.0.*$',ipv4['ip']):
                                        self.localip[device.hostname].append(ipv4['ip'])
        logFile=open('ipv4'+'.txt', 'w')
        pprint(self.localip,logFile)

    @aetest.test 
    def ipv4__connectivity(self, testbed, steps):
        for device in testbed.devices.values():
            if device.hostname !="hub":
                with steps.start('IPv4 connectivity from hub to %s' % device.hostname, continue_ = True):
                    assert '!!!' in testbed.devices.hub.execute(f'ping {self.localip[device.hostname][0]} repeat 10')

            
if __name__ == '__main__':
    import argparse
    from genie import testbed

    parser = argparse.ArgumentParser()
    parser.add_argument('--testbed', dest = 'testbed',
                        type = testbed.load)

    args, unknown = parser.parse_known_args()

    aetest.main(**vars(args))