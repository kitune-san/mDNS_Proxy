
# MIT License
# 
# Copyright (c) 2025 kitune-san
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import ipaddress
import netifaces
import socket
import struct
import logging
import time

interfaces = [
    # L3VPN (Wireguard) area
    {
        'ip': netifaces.ifaddresses('wg0')[netifaces.AF_INET][0]['addr'],
        'mask': '255.0.0.0',
        'forwardto': ['10.0.0.1'],          # another SSDP proxy in L3VPN network
        'reverse': False
    },

    # Local area
    {
        'ip': netifaces.ifaddresses('enx3897a43740cb')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('enx3897a43740cb')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['224.0.0.251'],   # multicast address
        'reverse': False
    },
    {
        'ip': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['224.0.0.251'],   # multicast address
        'reverse': False
    }

]

class MDNSAgency():
    def __init__(self, ip, forwardto, data, port=5353, timeout=5, buffer_size=4096):
        self._ip            = ip
        self._forwardto     = forwardto
        self._data          = data
        self._port          = port
        self._timeout       = timeout
        self._buffer_size   = buffer_size

        self._logger = logging.getLogger(__name__)
        self._logger.addHandler(logging.NullHandler())
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = True

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))
            sock.bind((self._ip, self._port))
            sock.settimeout(self._timeout)

            request_address = ipaddress.IPv4Network(self._data[1][0], strict=False)

            for ip in self._forwardto:
                if request_address != ipaddress.IPv4Network(ip, strict=False):
                    sock.sendto(self._data[0], (ip, self._port))
                    self._logger.debug('MDNSAgency - SEND: {} -> ({}, {}): {}'.format(self._ip, ip, self._port, self._data[0]))


class MDNSProxy:
    def __init__(self, interfaces, port=5353, multicast='224.0.0.251', timeout=5, buffer_size=4096):
        self._interfaces    = interfaces
        self._port          = port
        self._multicast     = multicast
        self._timeout       = timeout
        self._buffer_size   = buffer_size

        self._logger = logging.getLogger(__name__)
        self._logger.addHandler(logging.NullHandler())
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = True

    def start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', self._port))
            for interface in self._interfaces:
                sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, socket.inet_aton(self._multicast) + socket.inet_aton(interface['ip']))
            sock.settimeout(self._timeout)

            while True:
                try:
                    recieve = sock.recvfrom(self._buffer_size)

                    local_network   = False
                    same_address    = False
                    agencies = []
                    for interface in self._interfaces:
                        net1 = ipaddress.IPv4Network((interface['ip'], '255.255.255.255'), strict=False)
                        net2 = ipaddress.IPv4Network((recieve[1][0], '255.255.255.255'), strict=False)
                        if net1.network_address == net2.network_address:
                            same_address = True
                            break

                        net1 = ipaddress.IPv4Network((interface['ip'], interface['mask']), strict=False)
                        net2 = ipaddress.IPv4Network((recieve[1][0], interface['mask']), strict=False)

                        add_agency = False
                        if net1.network_address == net2.network_address:
                            local_network = True
                            if interface['reverse'] is True:
                                add_agency = True
                        else:
                            add_agency = True

                        if add_agency is True:
                           agencies.append(MDNSAgency(ip=interface['ip'], forwardto=interface['forwardto'], data=recieve,
                                                      port=self._port, timeout=self._timeout, buffer_size=self._buffer_size))

                    if local_network is True and same_address is False:
                        self._logger.debug('RECV: ({}, {}) {}'.format(recieve[1][0], recieve[1][1], recieve[0]))

                        for agency in agencies:
                            agency.start()

                except socket.timeout:
                    pass

if __name__ == '__main__':
    logger  = logging.getLogger()
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    mdns_proxy = MDNSProxy(interfaces)
    mdns_proxy.start()

