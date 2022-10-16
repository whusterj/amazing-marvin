import httpx

FULL_ACCESS_TOKEN = "V36m2PzxFwvS+P1VPdpbMm5MI4U="

API_BASE = "https://serv.amazingmarvin.com/api"


def test_api():
    endpoint = f"{API_BASE}/test"
    r = httpx.post(endpoint, headers={"X-API-Token": FULL_ACCESS_TOKEN})
    return r
