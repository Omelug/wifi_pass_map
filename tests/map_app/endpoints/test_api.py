import pytest
from map_app.endpoints.api import api_bp
from flask import Flask

@pytest.fixture
def client(monkeypatch):
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    app.config['TESTING'] = True

    # Mock sources.get_AP_data
    monkeypatch.setattr('map_app.sources.get_AP_data', lambda: ([{'id': 1}], {'status': 'ok'}))
    with app.test_client() as client:
        yield client

def test_wifi_pass_map(client):
    resp = client.get('/api/wifi_pass_map')
    assert resp.status_code == 200
    data = resp.get_json()
    assert 'data' in data
    assert 'script_statuses' in data
    assert 'AP_len' in data
    assert data['AP_len'] == 1

