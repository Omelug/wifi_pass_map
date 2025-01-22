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
    print(format_bssid('001122334455'))
    print(dec2mac(1122334455))
    print(mac2dec('00:11:22:33'))