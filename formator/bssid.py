import logging


def format_bssid(bssid:str) -> str:
    if len(bssid) != 12:
        raise ValueError("Invalid BSSID - invalid len")
    if not bssid.isalnum():
        raise ValueError("Invalid BSSID - invalid char")
    return ':'.join(bssid[i:i + 2] for i in range(0, len(bssid), 2))

def dec2mac(mac:int) -> str:
    mac = f'{mac:012x}'
    mac = mac.zfill(12)
    mac = ':'.join(mac[i:i+2] for i in range(0, 12, 2))
    return mac

def mac2dec(mac:str) -> int:
    mac = mac.replace(':', '').replace('-', '').replace('.', '')
    return int(mac, 16)

# This was stolen from pwnagotchi, thanks to the authors
def extract_essid_bssid(hash_line) -> tuple[str, str, str]:
    parts = hash_line.strip().split('*')

    essid = ''
    bssid = '00:00:00:00:00:00'
    password = None

    if len(parts) > 5:
        try:
            essid = bytes.fromhex(parts[5]).decode('utf-8', errors='replace')
        except ValueError as e:
            logging.error(f"Failed to decode ESSID from hex: {e}")

    if len(parts) > 4 and parts[4]:
        password = parts[4]

    if len(parts) > 3 and len(parts[3]) == 12:
        bssid = ':'.join(parts[3][i:i+2] for i in range(0, 12, 2))
    else:
        logging.error(f"Failed to extract BSSID from hash -> {hash_line}")

    return essid, bssid, password
