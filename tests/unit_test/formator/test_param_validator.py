from formator.param_validator import valid_wigle_key

# ---- WIGLE------
def test_wigle_key():
    assert valid_wigle_key("UlENDE1ZTI4ZTU0NDc1NzMwODljZjc2Zjg2MDM3ZDFhMWQ6YWRiNDM1MmVjMTQ1NmU5MzdlZWJlYWExOTU4ZTExZWQ")
    assert not valid_wigle_key("invalidWigleKey")