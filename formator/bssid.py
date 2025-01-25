def format_bssid(bssid):
    return ':'.join(bssid[i:i + 2] for i in range(0, len(bssid), 2))

def dec2mac(mac):
    mac = f'{mac:012x}'
    mac = mac.zfill(12)
    mac = ':'.join(mac[i:i+2] for i in range(0, 12, 2))
    return mac

def mac2dec(mac):
    mac = mac.replace(':', '').replace('-', '').replace('.', '')
    return int(mac, 16)


if __name__ == '__main__':
    m = dec2mac(136606244655)
    print(m)
    print(mac2dec(m))