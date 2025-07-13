import itertools
import requests
from typing import Optional

PROXY_SOURCES = {
    "http": "https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/refs/heads/main/http.txt",
    "https": "https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/refs/heads/main/https.txt",
    "socks4": "https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/refs/heads/main/socks4.txt",
    "socks5": "https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/refs/heads/main/socks5.txt",
}

class ProxyManager:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self.proxies = []
        self._iterator = None

    def download_proxies(self) -> None:
        collected = []
        for proto, url in PROXY_SOURCES.items():
            try:
                resp = requests.get(url, timeout=self.timeout)
                resp.raise_for_status()
                for line in resp.text.splitlines():
                    line = line.strip()
                    if line:
                        collected.append(f"{proto}://{line}")
            except requests.RequestException:
                continue
        self.proxies = [p for p in collected if self._validate_proxy(p)]
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

    def get_next_proxy(self) -> Optional[dict]:
        if not self._iterator:
            return None
        for _ in range(len(self.proxies)):
            proxy = next(self._iterator)
            if self._validate_proxy(proxy):
                return {"http": proxy, "https": proxy}
        return None
