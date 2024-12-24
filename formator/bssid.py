def format_bssid(bssid):
    return ':'.join(bssid[i:i + 2] for i in range(0, len(bssid), 2))