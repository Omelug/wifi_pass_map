from formator.param_validator import valid_wigle_key, valid_wpasec_key, valid_link


# ---- WIGLE------
def test_wigle_key():
    assert valid_wigle_key("UlENDE1ZTI4ZTU0NDc1NzMwODljZjc2Zjg2MDM3ZDFhMWQ6YWRiNDM1MmVjMTQ1NmU5MzdlZWJlYWExOTU4ZTExZWQ")
    assert not valid_wigle_key("invalidWigleKey")

def test_valid_wpasec_key():
    assert valid_wpasec_key("a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6")
    assert valid_wpasec_key("A1B2C3D4E5F6A7B8C9D0E1F2A3B4C5D6")
    assert not valid_wpasec_key("shortkey")
    assert not valid_wpasec_key("g1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6")  # 'g' is not hex

def test_valid_link():
    assert valid_link("http://example.com")
    assert valid_link("https://example.com/path?query=1")
    assert not valid_link("ftp://example.com")
    assert not valid_link("not_a_url")
    assert not valid_link("http:/example.com")