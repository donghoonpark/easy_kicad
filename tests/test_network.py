from __future__ import annotations

import requests

from easy_kicad.core.network import build_session, build_verify_value, patch_easyeda_requests
from easy_kicad.schemas.settings import AppSettings


def test_build_verify_value_prefers_ssl_ignore():
    settings = AppSettings(ignore_ssl_verification=True, ca_bundle_path="/tmp/custom.pem")
    assert build_verify_value(settings) is False


def test_build_verify_value_uses_ca_bundle():
    settings = AppSettings(ca_bundle_path="/tmp/custom.pem")
    assert build_verify_value(settings) == "/tmp/custom.pem"


def test_build_session_sets_proxy_and_verify():
    settings = AppSettings(
        proxy_url="http://127.0.0.1:8899",
        ca_bundle_path="/tmp/custom.pem",
    )

    session = build_session(settings)

    try:
        assert session.verify == "/tmp/custom.pem"
        assert session.proxies["http"] == "http://127.0.0.1:8899"
        assert session.proxies["https"] == "http://127.0.0.1:8899"
    finally:
        session.close()


def test_patch_easyeda_requests_passes_timeout_proxy_and_verify(monkeypatch):
    captured: dict[str, object] = {}

    def fake_session_get(self, *args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs

        class DummyResponse:
            status_code = 200

            def json(self):
                return {}

        return DummyResponse()

    monkeypatch.setattr(requests.Session, "get", fake_session_get)

    settings = AppSettings(
        proxy_url="http://127.0.0.1:8899",
        ca_bundle_path="/tmp/custom.pem",
        request_timeout_seconds=13,
    )

    from easyeda2kicad.easyeda import easyeda_api

    original_get = easyeda_api.requests.get
    with patch_easyeda_requests(settings):
        easyeda_api.requests.get("https://example.com/data")

    assert captured["kwargs"]["timeout"] == 13
    assert captured["kwargs"]["verify"] == "/tmp/custom.pem"
    assert captured["kwargs"]["proxies"] == {
        "http": "http://127.0.0.1:8899",
        "https": "http://127.0.0.1:8899",
    }
    assert easyeda_api.requests.get is original_get
