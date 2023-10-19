from app import app
from flask import Response
import json
import db.db as dbm

# Assuming that 'db' is an instance of your database
PATH = '/packages/stats'

def test_show_packages_endpoint(client):
    # Create a test client using the pytest-flask fixture
    client = app.test_client()

    # Simulate a call to the endpoint
    response = client.get(PATH + '/bioc/bioc_packages.txt')

    # Check the HTTP status code
    assert response.status_code == 200

    # Check the content type
    assert response.content_type == 'text/plain; charset=utf-8'

    # Assuming db.get_package_names() returns a dictionary with a 'package' key
    # Check if the response content matches the expected result
    expected_text = '\n'.join([row for row in dbm.get_package_names()['package']])
    assert response.data.decode('utf-8') == expected_text