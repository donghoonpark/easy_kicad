from __future__ import annotations

from contextlib import contextmanager
from typing import Union

import requests
import urllib3

from easy_kicad.schemas.settings import AppSettings

EASYEDA_BROWSER_HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://easyeda.com",
    "Referer": "https://easyeda.com/",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/135.0.0.0 Safari/537.36"
    ),
}


def build_verify_value(settings: AppSettings) -> Union[bool, str]:
    if settings.ignore_ssl_verification:
        return False
    if settings.ca_bundle_path:
        return settings.ca_bundle_path
    return True


def build_session(settings: AppSettings) -> requests.Session:
    session = requests.Session()
    session.verify = build_verify_value(settings)
    if settings.proxy_url:
        session.proxies.update(
            {
                "http": settings.proxy_url,
                "https": settings.proxy_url,
            }
        )
    if settings.ignore_ssl_verification:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return session


def merge_easyeda_headers(headers: dict[str, str] | None = None) -> dict[str, str]:
    merged_headers = dict(headers or {})
    merged_headers.update(EASYEDA_BROWSER_HEADERS)
    return merged_headers


@contextmanager
def patch_easyeda_requests(settings: AppSettings):
    from easyeda2kicad.easyeda import easyeda_api

    session = build_session(settings)
    original_get = easyeda_api.requests.get

    def session_get(*args, **kwargs):
        kwargs.setdefault("timeout", settings.request_timeout_seconds)
        kwargs.setdefault("verify", session.verify)
        if session.proxies:
            kwargs.setdefault("proxies", session.proxies)
        kwargs["headers"] = merge_easyeda_headers(kwargs.get("headers"))
        return session.get(*args, **kwargs)

    easyeda_api.requests.get = session_get
    try:
        yield
    finally:
        easyeda_api.requests.get = original_get
        session.close()
