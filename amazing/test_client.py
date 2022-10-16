import os

from amazing.main import AmazingCloudAntClient, api_test_endpoint


async def test_call_amazing_test_endpoint():
    r = await api_test_endpoint()
    assert r.status_code == 200


def test_cloudant_get_server_info():
    client = AmazingCloudAntClient()
    info = client.server_information()
    assert info["couchdb"] == "Welcome"


def test_cloudant_get_db_info():
    client = AmazingCloudAntClient()
    info = client.get_db_info()
    assert info


def test_cloudant_get_all_tasks():
    client = AmazingCloudAntClient()
    tasks = client.get_all_tasks()
    assert len(tasks) > 1500


def test_cloudant_get_task_stats():
    client = AmazingCloudAntClient()
    stats = client.get_task_stats()
    assert stats
