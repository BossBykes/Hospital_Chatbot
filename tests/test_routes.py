import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()


def test_home_page(client):
    res = client.get('/')
    assert res.status_code == 200


def test_api_get(client):
    res = client.post('/api/get', json={'message': 'When can I visit?'})
    assert res.status_code == 200
    data = res.get_json()
    assert 'response' in data


def test_appointment_booking_flow(client):
    res = client.post('/api/get', json={'message': 'can i book an appointment'})
    assert res.status_code == 200
    data = res.get_json()
    assert 'department' in data['response'].lower() or 'reason' in data['response'].lower()

    res = client.post('/api/get', json={'message': 'cardiology'})
    data = res.get_json()
    assert 'date' in data['response'].lower()

    res = client.post('/api/get', json={'message': '2026-02-10'})
    data = res.get_json()
    assert 'time' in data['response'].lower()

    res = client.post('/api/get', json={'message': 'morning'})
    data = res.get_json()
    assert 'confirm' in data['response'].lower() or 'yes' in data['response'].lower()

    res = client.post('/api/get', json={'message': 'yes'})
    data = res.get_json()
    assert 'confirm' in data['response'].lower() or 'book' in data['response'].lower()

    res = client.post('/api/get', json={'message': 'what is my appointment'})
    data = res.get_json()
    resp = data['response'].lower()
    assert 'cardiology' in resp
    assert '2026-02-10' in resp
    assert 'morning' in resp or '10' in resp or 'time' in resp


def test_appointment_cancel_flow(client):
    res = client.post('/api/get', json={'message': 'book an appointment'})
    data = res.get_json()
    assert 'department' in data['response'].lower() or 'reason' in data['response'].lower()

    res = client.post('/api/get', json={'message': 'cardiology'})
    data = res.get_json()
    assert 'date' in data['response'].lower()

    res = client.post('/api/get', json={'message': '2026-02-10'})
    data = res.get_json()
    assert 'time' in data['response'].lower()

    res = client.post('/api/get', json={'message': 'morning'})
    data = res.get_json()
    assert 'confirm' in data['response'].lower() or 'yes' in data['response'].lower()

    res = client.post('/api/get', json={'message': 'no'})
    data = res.get_json()
    assert 'cancel' in data['response'].lower()

    res = client.post('/api/get', json={'message': 'what is my appointment'})
    data = res.get_json()
    resp = data['response'].lower()
    assert 'no' in resp or 'none' in resp or 'book' in resp
