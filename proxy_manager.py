import itertools
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Set

import requests

PROXY_SOURCES = {
    "http": [
        "https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/refs/heads/main/http.txt",
        "https://raw.githubusercontent.com/casa-ls/proxy-list/refs/heads/main/http",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/refs/heads/main/proxy_files/http_proxies.txt",
        "https://github.com/databay-labs/free-proxy-list/raw/refs/heads/master/http.txt",
    ],
    "https": [
        "https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/refs/heads/main/https.txt",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/refs/heads/main/proxy_files/https_proxies.txt",
        "https://github.com/databay-labs/free-proxy-list/raw/refs/heads/master/https.txt",
    ],
    "socks4": [
        "https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/refs/heads/main/socks4.txt",
    ],
    "socks5": [
        "https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/refs/heads/main/socks5.txt",
    ],
}

class ProxyManager:
    def __init__(self, timeout: int = 5, max_usage: int = 5, workers: int = 30):
        self.timeout = timeout
        self.max_usage = max_usage
        self.workers = workers
        self.proxies: list[str] = []
        self.blacklist: Set[str] = set()
        self.usage_count: Dict[str, int] = {}
        self._iterator = None

    def download_proxies(self) -> None:
        collected = []
        for proto, urls in PROXY_SOURCES.items():
            for url in urls:
                try:
                    resp = requests.get(url, timeout=self.timeout)
                    resp.raise_for_status()
                    for line in resp.text.splitlines():
                        line = line.strip()
                        if line:
                            collected.append(f"{proto}://{line}")
                except requests.RequestException:
                    continue

        with ThreadPoolExecutor(max_workers=self.workers) as exc:
            results = list(exc.map(self._validate_proxy, collected))

        self.proxies = [p for p, ok in zip(collected, results) if ok]
        self.usage_count = {p: 0 for p in self.proxies}
        self.blacklist.clear()
        self._iterator = itertools.cycle(self.proxies) if self.proxies else None

    def _validate_proxy(self, proxy: str) -> bool:
        try:
            requests.get(
                "https://httpbin.org/ip",
                proxies={"http": proxy, "https": proxy},
                timeout=self.timeout,
            )
            return True
        except requests.RequestException:
            return False

    def _refresh_cycle(self) -> None:
        self.proxies = [p for p in self.proxies if p not in self.blacklist]
        self._iterator = itertools.cycle(self.proxies) if self.proxies else None

    def get_next_proxy(self) -> Optional[dict]:
        if not self._iterator:
            return None

        for _ in range(len(self.proxies)):
            proxy = next(self._iterator)
            if proxy in self.blacklist:
                continue

            count = self.usage_count.get(proxy, 0) + 1
            if count >= self.max_usage:
                self.blacklist.add(proxy)
                self.usage_count.pop(proxy, None)
                continue

            self.usage_count[proxy] = count
            return {"http": proxy, "https": proxy}

        self._refresh_cycle()
        return None
