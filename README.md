# mDNS_Proxy
mDNS Proxy for L3VPN(Wireguard) [EXPERIMENTAL]

## Configuration Example

### Pattern 1 - End-to-End

```
[Local area]---(eth0)(wg0:10.0.0.1)-------(VPN)-------(wg0:10.0.0.2)(eth0)---[Local area]
                                            |
                                            +---------(wg0:10.0.0.3)(eth0)---[Local area]
```


```python
# 10.0.0.1

interfaces = [
    # L3VPN (Wireguard) area
    {
        'ip': netifaces.ifaddresses('wg0')[netifaces.AF_INET][0]['addr'],   # 10.0.0.1
        'mask': '255.0.0.0',
        'forwardto': ['10.0.0.2', '10.0.0.3'],      # another SSDP proxy in L3VPN network
        'reverse': False
    },

    # Local area
    {
        'ip': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['239.255.255.250'],   # multicast address
        'reverse': False
    },
    {
        'ip': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['239.255.255.250'],   # multicast address
        'reverse': False
    }
]

```


```python
# 10.0.0.2

interfaces = [
    # L3VPN (Wireguard) area
    {
        'ip': netifaces.ifaddresses('wg0')[netifaces.AF_INET][0]['addr'],   # 10.0.0.2
        'mask': '255.0.0.0',
        'forwardto': ['10.0.0.1', '10.0.0.3'],      # another SSDP proxy in L3VPN network
        'reverse': False
    },

    # Local area
    {
        'ip': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['239.255.255.250'],   # multicast address
        'reverse': False
    },
    {
        'ip': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['239.255.255.250'],   # multicast address
        'reverse': False
    }
]

```

```python
# 10.0.0.3

interfaces = [
    # L3VPN (Wireguard) area
    {
        'ip': netifaces.ifaddresses('wg0')[netifaces.AF_INET][0]['addr'],   # 10.0.0.3
        'mask': '255.0.0.0',
        'forwardto': ['10.0.0.1', '10.0.0.2'],      # another SSDP proxy in L3VPN network
        'reverse': False
    },

    # Local area
    {
        'ip': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['239.255.255.250'],   # multicast address
        'reverse': False
    },
    {
        'ip': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['239.255.255.250'],   # multicast address
        'reverse': False
    }
]
```

### Pattern 2 - Reverse Proxy

```
(wg0:10.0.0.1 (reverse))------(VPN)-------(wg0:10.0.0.2 (client))(eth0)---[Local area]
                                |
                                +---------(wg0:10.0.0.3 (client))(eth0)---[Local area]
```

```python
# 10.0.0.1 (reverse)

interfaces = [
    # L3VPN (Wireguard) area
    {
        'ip': netifaces.ifaddresses('wg0')[netifaces.AF_INET][0]['addr'],   # 10.0.0.1
        'mask': '255.0.0.0',
        'forwardto': ['10.0.0.2', '10.0.0.3'],      # another SSDP proxy in L3VPN network
        'reverse': True
    }
]
```

```python
# 10.0.0.2

interfaces = [
    # L3VPN (Wireguard) area
    {
        'ip': netifaces.ifaddresses('wg0')[netifaces.AF_INET][0]['addr'],   # 10.0.0.2
        'mask': '255.0.0.0',
        'forwardto': ['10.0.0.1'],      # another SSDP proxy in L3VPN network
        'reverse': False
    },

    # Local area
    {
        'ip': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['239.255.255.250'],   # multicast address
        'reverse': False
    },
    {
        'ip': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['239.255.255.250'],   # multicast address
        'reverse': False
    }
]

```

```python
# 10.0.0.3

interfaces = [
    # L3VPN (Wireguard) area
    {
        'ip': netifaces.ifaddresses('wg0')[netifaces.AF_INET][0]['addr'],   # 10.0.0.3
        'mask': '255.0.0.0',
        'forwardto': ['10.0.0.1'],      # another SSDP proxy in L3VPN network
        'reverse': False
    },

    # Local area
    {
        'ip': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('eth0')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['239.255.255.250'],   # multicast address
        'reverse': False
    },
    {
        'ip': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['addr'],
        'mask': netifaces.ifaddresses('lo')[netifaces.AF_INET][0]['netmask'],
        'forwardto': ['239.255.255.250'],   # multicast address
        'reverse': False
    }
]
```

## Known issue

- Data sent from localhost is ignored.

