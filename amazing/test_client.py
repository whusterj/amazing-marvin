import os

from amazing.main import AmazingCloudAntClient, api_test_endpoint


async def test_call_amazing_test_endpoint():
    r = await api_test_endpoint()
    assert r.status_code == 200


def test_cloudant_get_server_info():
    client = AmazingCloudAntClient()
    info = client.server_information()
    assert info["couchdb"] == "Welcome"
