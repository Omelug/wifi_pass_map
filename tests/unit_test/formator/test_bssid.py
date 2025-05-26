import pytest
from formator import bssid

# ------- format_bssid -------
def test_format_bssid():
    assert bssid.format_bssid("aabbccddeeff") == "aa:bb:cc:dd:ee:ff"
    assert bssid.format_bssid("001122334455") == "00:11:22:33:44:55"

@pytest.mark.parametrize("invalid_bssid", [
    "aabbccddeef",      # invalid len
    "aabbccdd!eff",     # invalid char
    "aabbccdd eeff",    # space
])
def test_format_bssid_invalid(invalid_bssid):
    with pytest.raises(ValueError):
        bssid.format_bssid(invalid_bssid)

# ------- dec2mac -------
@pytest.mark.parametrize("dec,mac", [
    (0xAABBCCDDEEFF, "aa:bb:cc:dd:ee:ff"),
    (0x001122334455, "00:11:22:33:44:55"),
    (0, "00:00:00:00:00:00"),
])
def test_dec2mac(dec, mac):
    assert bssid.dec2mac(dec) == mac

# ------- mac2dec -------
@pytest.mark.parametrize("mac,dec", [
    ("aa:bb:cc:dd:ee:ff", 0xAABBCCDDEEFF),
    ("00-11-22-33-44-55", 0x001122334455),
    ("0011.2233.4455", 0x001122334455),
    ("00:00:00:00:00:00", 0),
])
def test_mac2dec(mac, dec):
    assert bssid.mac2dec(mac) == dec

def test_mac2dec_invalid():
    with pytest.raises(ValueError):
        bssid.mac2dec("invalid-mac")

# ------- extract_essid_bssid -------
def test_extract_essid_bssid_valid():
    # ESSID: "test" -> hex: 74657374, BSSID: aabbccddeeff, password: pass
    line = "x*x*x*aabbccddeeff*pass*74657374"
    essid, bssid_val, password = bssid.extract_essid_bssid(line)
    assert essid == "test"
    assert bssid_val == "aa:bb:cc:dd:ee:ff"
    assert password == "pass"

def test_extract_essid_bssid_missing_fields():
    # Not enough parts, should return defaults
    line = "x*x*x"
    essid, bssid_val, password = bssid.extract_essid_bssid(line)
    assert essid == ""
    assert bssid_val == "00:00:00:00:00:00"
    assert password is None

def test_extract_essid_bssid_invalid_bssid():
    # BSSID part not 12 chars
    line = "x*x*x*short*pass*74657374"
    essid, bssid_val, password = bssid.extract_essid_bssid(line)
    assert bssid_val == "00:00:00:00:00:00"

def test_extract_essid_bssid_invalid_essid_hex():
    # Invalid ESSID hex
    line = "x*x*x*aabbccddeeff*pass*nothex"
    essid, bssid_val, password = bssid.extract_essid_bssid(line)
    assert essid == ""  # Should fall back to empty string

def test_extract_essid_bssid_empty_password():
    # Password field empty
    line = "x*x*x*aabbccddeeff**74657374"
    essid, bssid_val, password = bssid.extract_essid_bssid(line)
    assert password is None