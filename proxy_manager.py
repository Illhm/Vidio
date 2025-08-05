import itertools
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Optional, Set
import requests

PROXY_SOURCES = {
    "http": [
        "https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/main/http.txt",
        "https://raw.githubusercontent.com/casa-ls/proxy-list/main/http",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/http_proxies.txt",
        "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/http.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt",
    ],
    "https": [
        "https://raw.githubusercontent.com/vmheaven/VMHeaven-Free-Proxy-Updated/main/https.txt",
        "https://raw.githubusercontent.com/Anonym0usWork1221/Free-Proxies/main/proxy_files/https_proxies.txt",
        "https://raw.githubusercontent.com/r00tee/Proxy-List/main/Https.txt",
        "https://raw.githubusercontent.com/databay-labs/free-proxy-list/master/https.txt",
    ],
}

class ProxyManager:
    def __init__(
        self,
        timeout: int = 3,
        max_usage: int = 5,
        workers: int = 150,
        fail_threshold: int = 3,
    ):
        self.timeout = timeout
        self.max_usage = max_usage
        self.workers = workers
        self.fail_threshold = fail_threshold
        self.proxies: list[str] = []
        self.blacklist: Set[str] = set()
        self.usage_count: Dict[str, int] = {}
        self.failures: Dict[str, int] = {}
        self._iterator = None

    def download_proxies(self) -> None:
        print("[ProxyManager] Mengunduh proxy dari sumber...")
        collected = []
        for proto, urls in PROXY_SOURCES.items():
            for url in urls:
                try:
                    print(f"[ProxyManager] Ambil dari {url}")
                    resp = requests.get(url, timeout=self.timeout)
                    resp.raise_for_status()
                    for line in resp.text.splitlines():
                        line = line.strip()
                        if line:
                            collected.append(f"{proto}://{line}")
                except requests.RequestException:
                    print(f"[ProxyManager] Gagal ambil dari {url}")
                    continue

        print(f"[ProxyManager] Total proxy terkumpul (mentah): {len(collected)}")
        collected = collected[:6000]  # Batasi untuk testing

        print("[ProxyManager] Validasi proxy...")
        with ThreadPoolExecutor(max_workers=self.workers) as exc:
            results = list(exc.map(self._validate_proxy, collected))

        self.proxies = [p for p, ok in zip(collected, results) if ok]
        print(f"[ProxyManager] Proxy valid: {len(self.proxies)}")

        self.usage_count = {p: 0 for p in self.proxies}
        self.failures.clear()
        self.blacklist.clear()
        self._iterator = itertools.cycle(self.proxies) if self.proxies else None

    def _validate_proxy(self, proxy: str) -> bool:
        try:
            response = requests.get(
                "https://httpbin.org/ip",
                proxies={"http": proxy, "https": proxy},
                timeout=self.timeout,
            )
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _refresh_cycle(self) -> None:
        print("[ProxyManager] Semua proxy sudah digunakan maksimal. Refresh siklus...")
        self.proxies = [p for p in self.proxies if p not in self.blacklist]
        self._iterator = itertools.cycle(self.proxies) if self.proxies else None

    def get_next_proxy(self) -> Optional[dict]:
        if not self._iterator:
            print("[ProxyManager] Tidak ada proxy valid tersedia.")
            return None

        for _ in range(len(self.proxies)):
            proxy = next(self._iterator)
            if proxy in self.blacklist:
                continue

            count = self.usage_count.get(proxy, 0)
            if count >= self.max_usage:
                print(f"[ProxyManager] Proxy mencapai batas penggunaan: {proxy}")
                self.blacklist.add(proxy)
                self.usage_count.pop(proxy, None)
                continue

            self.usage_count[proxy] = count + 1
            print(f"[ProxyManager] Menggunakan proxy: {proxy} (ke-{count + 1})")
            return {"http": proxy, "https": proxy}

        self._refresh_cycle()
        return None

    def report_failure(self, proxy: str) -> None:
        """Tambahkan penalti pada proxy yang gagal. Blacklist jika melewati ambang."""
        if proxy in self.blacklist:
            return
        failures = self.failures.get(proxy, 0) + 1
        if failures >= self.fail_threshold:
            print(f"[ProxyManager] Proxy gagal {failures} kali, blacklist: {proxy}")
            self.blacklist.add(proxy)
            self.usage_count.pop(proxy, None)
            self.failures.pop(proxy, None)
        else:
            self.failures[proxy] = failures
            print(f"[ProxyManager] Proxy gagal {failures} kali: {proxy}")
