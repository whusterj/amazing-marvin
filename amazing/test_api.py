from amazing.main import api_test_endpoint


async def test_call_amazing_test_endpoint():
    r = await api_test_endpoint()
    assert r.status_code == 200
