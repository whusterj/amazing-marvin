"""Shared Cloudant connection for the scripts in this folder.

AmazingCloudAntClient.client calls CloudantV1.new_instance(), which reads the
IBM SDK's own environment variable names. These scripts build the client from
the CLOUDANT_* names in .env instead, so one helper replaces the copy of this
code that every script used to carry.
"""

import datetime as dt
import os

from dotenv import load_dotenv
from ibm_cloud_sdk_core.authenticators import BasicAuthenticator
from ibmcloudant.cloudant_v1 import CloudantV1

from amazing.main import AmazingCloudAntClient

STAR_LABELS: dict[int, str] = {3: "P1", 2: "P2", 1: "P3"}


class EnvAuthClient(AmazingCloudAntClient):
    """AmazingCloudAntClient that authenticates from the CLOUDANT_* variables."""

    def __init__(self, service: CloudantV1):
        self._service = service

    @property
    def client(self) -> CloudantV1:
        return self._service


def get_client() -> EnvAuthClient:
    """Build a client from .env. Raises KeyError when a variable is absent."""
    load_dotenv()
    auth = BasicAuthenticator(username=os.environ["CLOUDANT_USERNAME"], password=os.environ["CLOUDANT_PASSWORD"])
    service = CloudantV1(authenticator=auth)
    service.service_url = os.environ["CLOUDANT_URL"]
    return EnvAuthClient(service)


def get_service() -> CloudantV1:
    """Build a bare CloudantV1 for scripts that query the database directly."""
    return get_client().client


def db_name() -> str:
    load_dotenv()
    return os.environ["CLOUDANT_SYNC_DB"]


def star(doc: dict) -> str:
    """Return the Marvin priority label for a task document."""
    starred = doc.get("isStarred")
    if not isinstance(starred, int):
        return "--"
    return STAR_LABELS.get(starred, "--")


def to_day(timestamp: int | None) -> str | None:
    """Convert a Marvin millisecond timestamp to a YYYY-MM-DD string."""
    if not timestamp:
        return None
    try:
        return dt.datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d")
    except (OverflowError, OSError, ValueError):
        return None
