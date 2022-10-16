import os

import httpx
from dotenv import load_dotenv
from ibmcloudant.cloudant_v1 import CloudantV1

load_dotenv()

API_BASE = "https://serv.amazingmarvin.com/api"


async def api_test_endpoint():
    """Test the Amazing Marvin API credentials."""
    endpoint = f"{API_BASE}/test"
    return httpx.post(
        endpoint,
        headers={"X-Full-Access-Token": os.environ.get("FULL_ACCESS_TOKEN")},
    )


class AmazingCloudAntClient:
    @property
    def client(self):
        return CloudantV1.new_instance()

    def server_information(self):
        return self.client.get_server_information().get_result()
