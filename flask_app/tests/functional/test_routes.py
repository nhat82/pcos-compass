''' Functional tests for routes ( ノ・・)ノ'''
from unittest.mock import patch

def test_home_route(client):
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode()
    assert "Welcome to PCOS Compass" in html
    
