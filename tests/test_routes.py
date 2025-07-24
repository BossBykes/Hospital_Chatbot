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