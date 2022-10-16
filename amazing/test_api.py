import pytest

from amazing.main import test_api


def test_call_amazing_test_endpoint():
    r = test_api()
    assert True
