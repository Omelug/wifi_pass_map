import logging


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

# This was stolen from pwnagotchi, thanks to the authors
def extract_essid_bssid(hash_line) -> tuple[str, str, str]:
    parts = hash_line.strip().split('*')

    essid = ''
    bssid = '00:00:00:00:00:00'
    password = None

    if len(parts) > 5:
        essid_hex = parts[5]
        try:
            essid = bytes.fromhex(essid_hex).decode('utf-8', errors='replace')
        except ValueError as e:
            logging.error(f"Failed to decode ESSID from hex: {e}")
            essid = ''

    if len(parts) > 4:
        password = parts[4] if parts[4] else None

    if len(parts) > 3:
        apmac = parts[3]
        if len(apmac) == 12:
            bssid = ':'.join(apmac[i:i + 2] for i in range(0, 12, 2))

    if bssid == '00:00:00:00:00:00':
        logging.error(f"Failed to extract BSSID from hash -> {hash_line}")

    return essid, bssid, password

if __name__ == '__main__':
    m = dec2mac(136606244655)
    print(m)
    print(mac2dec(m))