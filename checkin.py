#!/usr/bin/env python3
"""AnyRouter daily check-in helper."""

from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_BASE_URL = "https://anyrouter.top"
DEFAULT_CHECKIN_PATH = "/api/user/sign_in"
DEFAULT_INFO_PATH = "/api/v1/user/info"
TIMEOUT_SECONDS = 30


@dataclass
class HttpResult:
    status: int
    text: str
    json_body: Any | None


def env(name: str, default: str = "") -> str:
    value = os.getenv(name, "").strip()
    return value if value else default


def build_url(base_url: str, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def decode_json(text: str) -> Any | None:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def request_json(
    method: str,
    url: str,
    headers: dict[str, str],
    body: dict[str, Any] | None = None,
) -> HttpResult:
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url=url,
        data=data,
        headers=headers,
        method=method.upper(),
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS) as resp:
            text = resp.read().decode("utf-8", errors="replace")
            return HttpResult(resp.status, text, decode_json(text))
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", errors="replace")
        return HttpResult(exc.code, text, decode_json(text))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Network request failed: {exc}") from exc


def compact(value: Any, limit: int = 500) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return text if len(text) <= limit else text[:limit] + "..."


def extract_message(result: HttpResult) -> str:
    body = result.json_body
    if isinstance(body, dict):
        for key in ("message", "msg", "error", "data"):
            value = body.get(key)
            if isinstance(value, str) and value:
                return value
        return compact(body)
    return compact(result.text)


def make_headers(base_url: str) -> dict[str, str]:
    cookie = env("ANYROUTER_COOKIE")
    authorization = env("ANYROUTER_AUTHORIZATION")
    new_api_user = env("ANYROUTER_NEW_API_USER")

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": base_url.rstrip("/"),
        "Referer": base_url.rstrip("/") + "/",
        "User-Agent": env(
            "ANYROUTER_USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/126.0 Safari/537.36",
        ),
    }

    if cookie:
        headers["Cookie"] = cookie
    if new_api_user:
        headers["new-api-user"] = new_api_user

    if authorization:
        headers["Authorization"] = (
            authorization
            if authorization.lower().startswith(("bearer ", "basic "))
            else f"Bearer {authorization}"
        )

    return headers


def notify(title: str, content: str) -> None:
    send_key = env("SERVERCHAN_SENDKEY")
    pushplus_token = env("PUSHPLUS_TOKEN")

    if send_key:
        url = f"https://sctapi.ftqq.com/{urllib.parse.quote(send_key)}.send"
        data = urllib.parse.urlencode({"title": title, "desp": content}).encode()
        try:
            with urllib.request.urlopen(url, data=data, timeout=TIMEOUT_SECONDS):
                print("ServerChan notification sent.")
        except Exception as exc:
            print(f"ServerChan notification failed: {exc}", file=sys.stderr)

    if pushplus_token:
        url = "http://www.pushplus.plus/send"
        payload = json.dumps(
            {"token": pushplus_token, "title": title, "content": content}
        ).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT_SECONDS):
                print("PushPlus notification sent.")
        except Exception as exc:
            print(f"PushPlus notification failed: {exc}", file=sys.stderr)


def main() -> int:
    base_url = env("ANYROUTER_BASE_URL", DEFAULT_BASE_URL)
    checkin_path = env("ANYROUTER_CHECKIN_PATH", DEFAULT_CHECKIN_PATH)
    checkin_method = env("ANYROUTER_CHECKIN_METHOD", "POST")
    info_path = env("ANYROUTER_INFO_PATH", DEFAULT_INFO_PATH)

    if not env("ANYROUTER_COOKIE") and not env("ANYROUTER_AUTHORIZATION"):
        print(
            "Missing credential: set ANYROUTER_COOKIE or ANYROUTER_AUTHORIZATION.",
            file=sys.stderr,
        )
        return 2

    headers = make_headers(base_url)
    checkin_url = build_url(base_url, checkin_path)
    print(f"Check-in URL: {checkin_url}")

    started = time.time()
    result = request_json(checkin_method, checkin_url, headers)
    message = extract_message(result)
    elapsed = time.time() - started

    print(f"Check-in HTTP status: {result.status}")
    if message:
        print(f"Check-in message: {message}")

    info_message = ""
    if info_path:
        info_url = build_url(base_url, info_path)
        info_result = request_json("GET", info_url, headers)
        if 200 <= info_result.status < 300:
            info_message = extract_message(info_result)
            if info_message:
                print(f"User info: {info_message}")
        else:
            print(f"User info request skipped/failed: HTTP {info_result.status}")

    ok = 200 <= result.status < 300
    title = "AnyRouter check-in succeeded" if ok else "AnyRouter check-in failed"
    content = "\n".join(
        part
        for part in (
            f"Status: HTTP {result.status}",
            f"Message: {message}" if message else "",
            f"Info: {info_message}" if info_message else "",
            f"Elapsed: {elapsed:.2f}s",
        )
        if part
    )
    notify(title, content)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

